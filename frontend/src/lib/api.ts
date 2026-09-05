/**
 * KrishiX API Client
 * All requests use relative /api/* paths — Vite proxies them to the backend.
 * No env var baking. Works identically in Docker and local dev.
 */

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
}

async function makeRequest<T = unknown>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const token = localStorage.getItem("access_token");
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(endpoint, {
    ...options,
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
    }
    let message = `${response.status}`;
    try {
      const err = await response.json();
      message = err.detail || err.message || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

// ── Auth ────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (email: string, password: string) =>
    makeRequest("/api/auth/register", { method: "POST", body: { email, password } }),
  login: (email: string, password: string) =>
    makeRequest<{ access_token: string; token_type: string }>("/api/auth/login", {
      method: "POST", body: { email, password },
    }),
  logout: () => makeRequest("/api/auth/logout", { method: "POST" }),
};

// ── Users ───────────────────────────────────────────────────────────────────
export const userAPI = {
  getCurrentUser: () => makeRequest<{ id: string; email: string }>("/api/users/me"),
  changePassword: (current_password: string, new_password: string) =>
    makeRequest("/api/users/me/password", {
      method: "PUT", body: { current_password, new_password },
    }),
};

// ── Farmer Profile ──────────────────────────────────────────────────────────
export const farmerProfileAPI = {
  getProfile: () => makeRequest<any>("/api/farmer-profile"),
  createProfile: (data: unknown) =>
    makeRequest("/api/farmer-profile", { method: "POST", body: data }),
  updateProfile: (data: unknown) =>
    makeRequest("/api/farmer-profile", { method: "PUT", body: data }),
};

// ── Commodities ─────────────────────────────────────────────────────────────
export const commodityAPI = {
  listCommodities: (category?: string, limit = 20, offset = 0) => {
    const p = new URLSearchParams();
    if (category) p.append("category", category);
    p.append("limit", String(limit));
    p.append("offset", String(offset));
    return makeRequest<{ total: number; items: any[] }>(`/api/commodities?${p}`);
  },
  getCommodity: (id: string) => makeRequest<any>(`/api/commodities/${id}`),
};

// ── Markets ─────────────────────────────────────────────────────────────────
export const marketAPI = {
  listMarkets: (state: string, district?: string, limit = 20, offset = 0) => {
    const p = new URLSearchParams({ state });
    if (district) p.append("district", district);
    p.append("limit", String(limit));
    p.append("offset", String(offset));
    return makeRequest<{ total: number; items: any[] }>(`/api/markets?${p}`);
  },
  getMarket: (id: string) => makeRequest<any>(`/api/markets/${id}`),
};

// ── Market Prices ───────────────────────────────────────────────────────────
export const priceAPI = {
  getLatestPrices: (filters: {
    state?: string; district?: string; market_id?: string;
    commodity_id?: string; date?: string; limit?: number; offset?: number;
  }) => {
    const p = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v != null) p.append(k, String(v)); });
    return makeRequest<{ total: number; items: any[] }>(`/api/market-prices?${p}`);
  },
  comparePrices: (commodityId: string, state?: string, district?: string, date?: string) => {
    const p = new URLSearchParams({ commodity_id: commodityId });
    if (state) p.append("state", state);
    if (district) p.append("district", district);
    if (date) p.append("date", date);
    return makeRequest<any>(`/api/market-prices/compare?${p}`);
  },
  getPriceHistory: (marketId: string, commodityId: string, days = 30) => {
    const p = new URLSearchParams({ market_id: marketId, commodity_id: commodityId, days: String(days) });
    return makeRequest<any>(`/api/market-prices/history?${p}`);
  },
};

// ── Selling Decision ────────────────────────────────────────────────────────
export const decisionAPI = {
  getDecision: (params: {
    commodity_id: string; quantity_quintal: number;
    farmer_lat: number; farmer_lon: number; state?: string;
  }) => {
    const p = new URLSearchParams({
      commodity_id: params.commodity_id,
      quantity_quintal: String(params.quantity_quintal),
      farmer_lat: String(params.farmer_lat),
      farmer_lon: String(params.farmer_lon),
    });
    if (params.state) p.append("state", params.state);
    return makeRequest<any>(`/api/selling-decision?${p}`);
  },
};

// ── Buyers ──────────────────────────────────────────────────────────────────
export const buyerAPI = {
  listBuyers: (commodity?: string, state?: string) => {
    const p = new URLSearchParams();
    if (commodity) p.append("commodity", commodity);
    if (state) p.append("state", state);
    return makeRequest<{ total: number; items: any[] }>(`/api/buyers?${p}`);
  },
};

// ── Saved ───────────────────────────────────────────────────────────────────
export const savedAPI = {
  getSavedMarkets: (limit = 20, offset = 0) => {
    const p = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    return makeRequest<{ total: number; items: any[] }>(`/api/saved-markets?${p}`);
  },
  saveMarket: (marketId: string) =>
    makeRequest(`/api/saved-markets/${marketId}`, { method: "POST" }),
  unsaveMarket: (marketId: string) =>
    makeRequest(`/api/saved-markets/${marketId}`, { method: "DELETE" }),
  getSavedCommodities: (limit = 20, offset = 0) => {
    const p = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    return makeRequest<{ total: number; items: any[] }>(`/api/saved-commodities?${p}`);
  },
  saveCommodity: (commodityId: string) =>
    makeRequest(`/api/saved-commodities/${commodityId}`, { method: "POST" }),
  unsaveCommodity: (commodityId: string) =>
    makeRequest(`/api/saved-commodities/${commodityId}`, { method: "DELETE" }),
};
