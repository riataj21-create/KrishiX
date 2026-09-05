"""
Weather API — Open-Meteo proxy with transport risk assessment.

Open-Meteo is completely free, no API key required.
Source: https://open-meteo.com/

The backend proxies the call so:
- The frontend never calls an external API directly
- We can add caching/fallback in one place
- The response is normalised and transport-risk-assessed here

All data is labelled with its actual source and observation timestamp.
Nothing is called "LIVE" — Open-Meteo updates hourly, so data is "RECENT".
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger("krishix.weather")

router = APIRouter()

# ---------------------------------------------------------------------------
# Transport-risk thresholds (documented assumptions, not magic numbers)
# Source: general agricultural logistics practice
# Scope: all regions, all commodities (crop-specific overrides can be added)
# ---------------------------------------------------------------------------
RAIN_RISK_THRESHOLD_MM = 5.0    # mm precipitation in next 24h → HIGH risk
TEMP_HIGH_RISK_C = 38.0         # °C ambient → spoilage risk for perishables
TEMP_LOW_RISK_C = 5.0           # °C ambient → frost risk for some produce

# Open-Meteo endpoint — no key required
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _assess_transport_risk(
    current_temp_c: float,
    precipitation_next_24h_mm: float,
    wind_speed_kmh: float,
) -> dict:
    """
    Produce a transport risk signal based on weather conditions.
    Returns an explainable signal rather than an opaque score.
    """
    risks = []
    level = "LOW"

    if precipitation_next_24h_mm >= RAIN_RISK_THRESHOLD_MM:
        risks.append(
            f"Rain expected ({precipitation_next_24h_mm:.1f} mm in next 24h) — "
            "increased road risk and moisture exposure for open vehicles"
        )
        level = "HIGH" if precipitation_next_24h_mm >= 15 else "MEDIUM"

    if current_temp_c >= TEMP_HIGH_RISK_C:
        risks.append(
            f"High ambient temperature ({current_temp_c:.1f}°C) — "
            "accelerates spoilage for perishables in unventilated transport"
        )
        if level != "HIGH":
            level = "MEDIUM"

    if current_temp_c <= TEMP_LOW_RISK_C:
        risks.append(
            f"Low temperature ({current_temp_c:.1f}°C) — "
            "frost risk for temperature-sensitive produce"
        )
        if level == "LOW":
            level = "MEDIUM"

    if wind_speed_kmh >= 50:
        risks.append(
            f"Strong winds ({wind_speed_kmh:.0f} km/h) — "
            "risk for open-truck transport of lightweight produce"
        )
        if level == "LOW":
            level = "MEDIUM"

    if not risks:
        risks.append("Weather conditions are within normal range for transport")

    return {
        "risk_level": level,          # LOW | MEDIUM | HIGH
        "risk_factors": risks,
        "sell_signal": (
            "SELL NOW — adverse weather may worsen transport conditions"
            if level == "HIGH"
            else "CONDITIONS NORMAL" if level == "LOW"
            else "MONITOR — marginal conditions, check before departure"
        ),
    }


def _build_fallback_response(lat: float, lon: float, reason: str) -> dict:
    """
    Return a clearly labelled degraded response when Open-Meteo is unavailable.
    Never fabricates weather data — always explicit about fallback status.
    """
    return {
        "data_status": "UNAVAILABLE",
        "data_source": "Open-Meteo (unavailable)",
        "fallback_reason": reason,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "location": {"latitude": lat, "longitude": lon},
        "current": None,
        "forecast_24h": None,
        "transport_risk": {
            "risk_level": "UNKNOWN",
            "risk_factors": ["Weather data unavailable — assess conditions manually before transport"],
            "sell_signal": "WEATHER UNAVAILABLE — check manually",
        },
        "message": "Weather service is currently unavailable. Transport risk cannot be assessed automatically.",
    }


@router.get("/weather")
async def get_weather(
    lat: float = Query(..., ge=-90, le=90, description="Latitude of farmer/farm location"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude of farmer/farm location"),
):
    """
    Fetch current weather and 24-hour forecast for a location.
    Assesses transport risk for agricultural produce.

    Data source: Open-Meteo (https://open-meteo.com/)
    Update frequency: Hourly
    Data label: RECENT (not LIVE — reflects last hourly update from Open-Meteo)
    No API key required.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "hourly": [
            "temperature_2m",
            "precipitation_probability",
            "precipitation",
        ],
        "forecast_days": 2,
        "timezone": "auto",
        "wind_speed_unit": "kmh",
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(OPEN_METEO_URL, params=params)
            resp.raise_for_status()
            raw = resp.json()
    except httpx.TimeoutException:
        logger.warning("Open-Meteo timeout for lat=%s lon=%s", lat, lon)
        return _build_fallback_response(lat, lon, "Request timed out after 8 seconds")
    except httpx.HTTPStatusError as exc:
        logger.warning("Open-Meteo HTTP error %s for lat=%s lon=%s", exc.response.status_code, lat, lon)
        return _build_fallback_response(lat, lon, f"Open-Meteo returned HTTP {exc.response.status_code}")
    except Exception as exc:
        logger.warning("Open-Meteo unexpected error for lat=%s lon=%s: %s", lat, lon, str(exc))
        return _build_fallback_response(lat, lon, "Unexpected error contacting weather service")

    # ── Parse current conditions ────────────────────────────────────────────
    current_raw = raw.get("current", {})
    current_vals = raw.get("current_units", {})

    temp_c: float = current_raw.get("temperature_2m", 25.0)
    humidity_pct: float = current_raw.get("relative_humidity_2m", 60.0)
    precip_now_mm: float = current_raw.get("precipitation", 0.0)
    wind_kmh: float = current_raw.get("wind_speed_10m", 0.0)
    weather_code: int = current_raw.get("weather_code", 0)
    observed_at: str = current_raw.get("time", datetime.now(timezone.utc).isoformat())

    # ── Sum precipitation over next 24 hours ───────────────────────────────
    hourly = raw.get("hourly", {})
    hourly_times = hourly.get("time", [])
    hourly_precip = hourly.get("precipitation", [])
    now_iso = observed_at[:13]  # "YYYY-MM-DDTHH"

    precip_next_24h = 0.0
    count = 0
    for i, t in enumerate(hourly_times):
        if t >= now_iso and count < 24 and i < len(hourly_precip):
            precip_next_24h += hourly_precip[i] or 0.0
            count += 1

    # ── WMO weather code → description ─────────────────────────────────────
    wmo_descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }
    condition = wmo_descriptions.get(weather_code, f"WMO code {weather_code}")

    transport_risk = _assess_transport_risk(temp_c, precip_next_24h, wind_kmh)

    return {
        "data_status": "RECENT",
        "data_source": "Open-Meteo (https://open-meteo.com/)",
        "data_note": "Open-Meteo updates hourly. This reflects the latest available observation, not real-time streaming data.",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "observed_at": observed_at,
        "location": {
            "latitude": lat,
            "longitude": lon,
            "timezone": raw.get("timezone", "UTC"),
        },
        "current": {
            "temperature_c": round(temp_c, 1),
            "humidity_pct": round(humidity_pct, 1),
            "precipitation_mm": round(precip_now_mm, 2),
            "wind_speed_kmh": round(wind_kmh, 1),
            "condition": condition,
            "weather_code": weather_code,
        },
        "forecast_24h": {
            "total_precipitation_mm": round(precip_next_24h, 2),
            "rain_expected": precip_next_24h >= RAIN_RISK_THRESHOLD_MM,
        },
        "transport_risk": transport_risk,
    }
