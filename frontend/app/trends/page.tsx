/**
 * Price Trends Page
 * Visualize historical commodity prices with Recharts
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Loader2, Calendar } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { marketAPI, commodityAPI, priceAPI } from "@/lib/api";

export default function TrendsPage() {
  const router = useRouter();

  const [markets, setMarkets] = useState<any[]>([]);
  const [commodities, setCommodities] = useState<any[]>([]);
  const [marketId, setMarketId] = useState("");
  const [commodityId, setCommodityId] = useState("");
  const [trendData, setTrendData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [state, setState] = useState("Punjab");

  // Check auth
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/auth/login");
    }
  }, [router]);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      // Load markets
      const marketResponse = await marketAPI.listMarkets(state);
      setMarkets(marketResponse.items || []);
      if (marketResponse.items && marketResponse.items.length > 0) {
        setMarketId(marketResponse.items[0].id);
      }

      // Load commodities
      const commodityResponse = await commodityAPI.listCommodities(
        undefined,
        100
      );
      setCommodities(commodityResponse.items || []);
      if (commodityResponse.items && commodityResponse.items.length > 0) {
        setCommodityId(commodityResponse.items[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleStateChange = async (newState: string) => {
    setState(newState);
    try {
      const marketResponse = await marketAPI.listMarkets(newState);
      setMarkets(marketResponse.items || []);
      if (marketResponse.items && marketResponse.items.length > 0) {
        setMarketId(marketResponse.items[0].id);
      }
      setTrendData([]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleViewTrend = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!marketId || !commodityId) {
      setError("Please select both market and commodity");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await priceAPI.getPriceHistory(marketId, commodityId, 30);
      setTrendData(
        response.trend.map((item: any) => ({
          date: new Date(item.date).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
          }),
          minPrice: item.min_price,
          modalPrice: item.modal_price,
          maxPrice: item.max_price,
        }))
      );

      if (response.trend.length === 0) {
        setError("No historical data available for this selection");
      }
    } catch (err: any) {
      setError("Failed to load trend data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Get selected commodity and market names
  const selectedCommodity = commodities.find((c) => c.id === commodityId);
  const selectedMarket = markets.find((m) => m.id === marketId);

  // Calculate statistics
  const stats =
    trendData.length > 0
      ? {
          highest: Math.max(...trendData.map((d) => d.maxPrice)),
          lowest: Math.min(...trendData.map((d) => d.minPrice)),
          average: (
            trendData.reduce((sum, d) => sum + d.modalPrice, 0) /
            trendData.length
          ).toFixed(2),
          change: (
            trendData[trendData.length - 1].modalPrice - trendData[0].modalPrice
          ).toFixed(2),
        }
      : null;

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <section className="bg-white border-b border-neutral-200">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <h1 className="text-h3 mb-2">Price Trends</h1>
          <p className="text-neutral-600">
            Visualize 30-day commodity price history
          </p>

          {/* Selection Form */}
          <form onSubmit={handleViewTrend} className="mt-8 space-y-4">
            <div className="grid md:grid-cols-4 gap-4">
              {/* State Selection */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  State
                </label>
                <select
                  className="input"
                  value={state}
                  onChange={(e) => handleStateChange(e.target.value)}
                >
                  <option value="Punjab">Punjab</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Haryana">Haryana</option>
                </select>
              </div>

              {/* Market Selection */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Market
                </label>
                <select
                  className="input"
                  value={marketId}
                  onChange={(e) => setMarketId(e.target.value)}
                >
                  <option value="">Select market</option>
                  {markets.map((market) => (
                    <option key={market.id} value={market.id}>
                      {market.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Commodity Selection */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Commodity
                </label>
                <select
                  className="input"
                  value={commodityId}
                  onChange={(e) => setCommodityId(e.target.value)}
                >
                  <option value="">Select commodity</option>
                  {commodities.map((commodity) => (
                    <option key={commodity.id} value={commodity.id}>
                      {commodity.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* View Button */}
              <div className="flex items-end">
                <button
                  type="submit"
                  className="btn-primary w-full"
                  disabled={loading || !marketId || !commodityId}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    "View Trend"
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>
      </section>

      {/* Main Content */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        {error && (
          <div className="bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg flex gap-3 mb-6">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary mb-4" />
            <p className="text-neutral-600">Loading price history...</p>
          </div>
        )}

        {!loading && trendData.length > 0 && stats && (
          <>
            {/* Statistics Cards */}
            <div className="grid md:grid-cols-4 gap-4 mb-8">
              <div className="card">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">HIGHEST PRICE</p>
                  <p className="text-h5 text-primary">₹{stats.highest.toLocaleString()}</p>
                </div>
              </div>

              <div className="card">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">LOWEST PRICE</p>
                  <p className="text-h5 text-danger">₹{stats.lowest.toLocaleString()}</p>
                </div>
              </div>

              <div className="card">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">30-DAY AVERAGE</p>
                  <p className="text-h5">₹{stats.average}</p>
                </div>
              </div>

              <div className="card">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">CHANGE</p>
                  <p className={`text-h5 ${Number(stats.change) >= 0 ? "text-success" : "text-danger"}`}>
                    {Number(stats.change) >= 0 ? "+" : ""}₹{stats.change}
                  </p>
                </div>
              </div>
            </div>

            {/* Chart Section */}
            <div className="card mb-8">
              <div className="card-header">
                <h3 className="text-h5">
                  {selectedCommodity?.name} in {selectedMarket?.name}
                </h3>
                <p className="text-sm text-neutral-600 mt-1">
                  Last 30 days • Min/Modal/Max prices
                </p>
              </div>

              <div className="card-body">
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                      dataKey="date"
                      stroke="#6b7280"
                      style={{ fontSize: "0.875rem" }}
                    />
                    <YAxis
                      stroke="#6b7280"
                      style={{ fontSize: "0.875rem" }}
                      label={{ value: "Price (₹)", angle: -90, position: "insideLeft" }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#fff",
                        border: "1px solid #e5e7eb",
                        borderRadius: "8px",
                      }}
                      formatter={(value) => `₹${value.toLocaleString()}`}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="minPrice"
                      stroke="#ef4444"
                      strokeWidth={2}
                      name="Min Price"
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="modalPrice"
                      stroke="#065f46"
                      strokeWidth={3}
                      name="Modal Price"
                      dot={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="maxPrice"
                      stroke="#10b981"
                      strokeWidth={2}
                      name="Max Price"
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="card-footer text-xs text-neutral-500">
                <Calendar className="inline w-3 h-3 mr-1" />
                Last 30 days of data from APMC {selectedMarket?.name}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 flex-wrap">
              <button
                onClick={() => setTrendData([])}
                className="btn-outline"
              >
                View Another Trend
              </button>
              <a href="/comparison" className="btn-outline">
                Compare Markets
              </a>
              <a href="/dashboard" className="btn-outline">
                Back to Dashboard
              </a>
            </div>
          </>
        )}

        {/* Empty State */}
        {!loading && trendData.length === 0 && (
          <div className="text-center py-12">
            <Calendar className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
            <h3 className="text-h5 text-neutral-700 mb-2">
              Select market and commodity
            </h3>
            <p className="text-neutral-600">
              Choose options above to view 30-day price trends
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
