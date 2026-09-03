/**
 * Price Comparison Page
 * Compare one commodity across multiple markets
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Bookmark, BookmarkCheck, Loader2, TrendingDown, TrendingUp } from "lucide-react";
import { commodityAPI, priceAPI, savedAPI } from "@/lib/api";

export default function ComparisonPage() {
  const router = useRouter();

  const [state, setState] = useState("Punjab");
  const [commodityId, setCommodityId] = useState("");
  const [commodities, setCommodities] = useState<any[]>([]);
  const [prices, setPrices] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedCommodity, setSelectedCommodity] = useState<any>(null);
  const [savedMarketIds, setSavedMarketIds] = useState<Set<string>>(new Set());

  // Check auth
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) router.push("/auth/login");
  }, [router]);

  // Load commodities + already-saved markets
  useEffect(() => {
    loadCommodities();
    savedAPI.getSavedMarkets(100, 0)
      .then((res: any) => {
        const ids = (res.items || []).map((i: any) => i.market_id as string);
        setSavedMarketIds(new Set(ids));
      })
      .catch(() => {});
  }, []);

  const loadCommodities = async () => {
    try {
      const response = await commodityAPI.listCommodities(undefined, 100);
      setCommodities(response.items || []);
      
      // Set first commodity as default
      if (response.items && response.items.length > 0) {
        setCommodityId(response.items[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!commodityId) {
      setError("Please select a commodity");
      return;
    }

    try {
      setLoading(true);
      setError("");

      // Get selected commodity details
      const commodity = commodities.find((c) => c.id === commodityId);
      setSelectedCommodity(commodity);

      // Get price comparison
      const response = await priceAPI.comparePrices(commodityId, state);
      setPrices(response.prices || []);

      if (response.prices && response.prices.length === 0) {
        setError(`No price data available for ${commodity?.name} in ${state}`);
      }
    } catch (err: any) {
      setError("Failed to load comparison data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Find best and worst prices
  const bestPrice =
    prices.length > 0
      ? prices.reduce((prev, current) =>
          prev.modal_price > current.modal_price ? prev : current
        )
      : null;

  const worstPrice =
    prices.length > 0
      ? prices.reduce((prev, current) =>
          prev.modal_price < current.modal_price ? prev : current
        )
      : null;

  const avgPrice =
    prices.length > 0
      ? (prices.reduce((sum, p) => sum + (p.modal_price || 0), 0) /
          prices.length)
        .toFixed(2)
      : 0;

  const potentialGain =
    bestPrice && worstPrice ? Math.round((bestPrice.modal_price - worstPrice.modal_price) * 1000) : 0;

  async function handleSaveMarket(marketId: string) {
    try {
      await savedAPI.saveMarket(marketId);
      setSavedMarketIds((prev) => new Set([...prev, marketId]));
    } catch {}
  }

  async function handleUnsaveMarket(marketId: string) {
    try {
      await savedAPI.unsaveMarket(marketId);
      setSavedMarketIds((prev) => { const n = new Set(prev); n.delete(marketId); return n; });
    } catch {}
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <section className="bg-white border-b border-neutral-200">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <h1 className="text-h3 mb-2">Price Comparison</h1>
          <p className="text-neutral-600">
            Compare commodity prices across multiple APMC markets
          </p>

          {/* Search Form */}
          <form onSubmit={handleCompare} className="mt-8 space-y-4">
            <div className="grid md:grid-cols-3 gap-4">
              {/* Commodity Selection */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Commodity *
                </label>
                <select
                  className="input"
                  value={commodityId}
                  onChange={(e) => setCommodityId(e.target.value)}
                >
                  <option value="">Select a commodity</option>
                  {commodities.map((commodity) => (
                    <option key={commodity.id} value={commodity.id}>
                      {commodity.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* State Selection */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  State
                </label>
                <select
                  className="input"
                  value={state}
                  onChange={(e) => setState(e.target.value)}
                >
                  <option value="Punjab">Punjab</option>
                  <option value="Maharashtra">Maharashtra</option>
                  <option value="Haryana">Haryana</option>
                  <option value="Uttar Pradesh">Uttar Pradesh</option>
                </select>
              </div>

              {/* Compare Button */}
              <div className="flex items-end">
                <button
                  type="submit"
                  className="btn-primary w-full"
                  disabled={loading || !commodityId}
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 w-4 h-4 animate-spin" />
                      Comparing...
                    </>
                  ) : (
                    "Compare Prices"
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
            <p className="text-neutral-600">Comparing prices...</p>
          </div>
        )}

        {!loading && prices.length > 0 && selectedCommodity && (
          <>
            {/* Summary Cards */}
            <div className="grid md:grid-cols-4 gap-4 mb-8">
              <div className="card">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">COMMODITY</p>
                  <p className="text-h5 text-primary">{selectedCommodity.name}</p>
                </div>
              </div>

              <div className="card border-l-4 border-l-success">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">BEST PRICE</p>
                  <p className="text-h5">₹{bestPrice?.modal_price.toLocaleString()}</p>
                  <p className="text-xs text-neutral-500 mt-2">
                    {bestPrice?.market_name}
                  </p>
                </div>
              </div>

              <div className="card border-l-4 border-l-danger">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">LOWEST PRICE</p>
                  <p className="text-h5">₹{worstPrice?.modal_price.toLocaleString()}</p>
                  <p className="text-xs text-neutral-500 mt-2">
                    {worstPrice?.market_name}
                  </p>
                </div>
              </div>

              <div className="card border-l-4 border-l-warning">
                <div className="card-body">
                  <p className="text-xs text-neutral-600 mb-1">AVG PRICE</p>
                  <p className="text-h5">₹{avgPrice}</p>
                  <p className="text-xs text-neutral-500 mt-2">
                    {prices.length} markets
                  </p>
                </div>
              </div>
            </div>

            {/* Potential Gain Alert */}
            {potentialGain > 0 && (
              <div className="bg-success/10 border border-success/30 text-success px-4 py-4 rounded-lg mb-8 flex gap-3">
                <TrendingUp className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Potential Gain</p>
                  <p className="text-sm">
                    Selling at best price vs worst: ₹{potentialGain} per quintal
                  </p>
                </div>
              </div>
            )}

            {/* Price Comparison Table */}
            <div className="card mb-8">
              <div className="card-header">
                <h3 className="text-h5">Market Comparison</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-neutral-50 border-b border-neutral-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-900">
                        Market
                      </th>
                      <th className="px-6 py-3 text-left text-sm font-semibold text-neutral-900">
                        Location
                      </th>
                      <th className="px-6 py-3 text-right text-sm font-semibold text-neutral-900">
                        Min Price
                      </th>
                      <th className="px-6 py-3 text-right text-sm font-semibold text-neutral-900">
                        Modal Price
                      </th>
                      <th className="px-6 py-3 text-right text-sm font-semibold text-neutral-900">
                        Max Price
                      </th>
                      <th className="px-6 py-3 text-center text-sm font-semibold text-neutral-900">
                        Status
                      </th>
                      <th className="px-6 py-3 text-center text-sm font-semibold text-neutral-900">
                        Save
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-200">
                    {prices.map((price) => {
                      const isBest =
                        price.modal_price === bestPrice?.modal_price;
                      const isWorst =
                        price.modal_price === worstPrice?.modal_price;

                      return (
                        <tr
                          key={price.market_id}
                          className={`${
                            isBest ? "bg-success/5" : isWorst ? "bg-danger/5" : ""
                          }`}
                        >
                          <td className="px-6 py-4 font-medium text-neutral-900">
                            {price.market_name}
                          </td>
                          <td className="px-6 py-4 text-neutral-600">
                            {price.state}, {price.district}
                          </td>
                          <td className="px-6 py-4 text-right text-neutral-900">
                            ₹{price.min_price.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-right font-semibold text-neutral-900">
                            ₹{price.modal_price.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-right text-neutral-900">
                            ₹{price.max_price.toLocaleString()}
                          </td>
                          <td className="px-6 py-4 text-center">
                            {isBest && <span className="badge-success">Best</span>}
                            {isWorst && <span className="badge-danger">Lowest</span>}
                          </td>
                          <td className="px-6 py-4 text-center">
                            <button
                              onClick={() =>
                                savedMarketIds.has(price.market_id)
                                  ? handleUnsaveMarket(price.market_id)
                                  : handleSaveMarket(price.market_id)
                              }
                              aria-label={savedMarketIds.has(price.market_id) ? "Remove saved market" : "Save market"}
                              className={`inline-flex h-8 w-8 items-center justify-center rounded transition-colors ${
                                savedMarketIds.has(price.market_id)
                                  ? "text-[var(--accent)] hover:text-[var(--error)]"
                                  : "text-[var(--text-muted)] hover:text-[var(--accent)]"
                              }`}
                            >
                              {savedMarketIds.has(price.market_id)
                                ? <BookmarkCheck size={17} />
                                : <Bookmark size={17} />}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 flex-wrap">
              <button
                onClick={() => setPrices([])}
                className="btn-outline"
              >
                Compare Another
              </button>
              <a href="/dashboard" className="btn-outline">
                Back to Dashboard
              </a>
            </div>
          </>
        )}

        {/* Empty State */}
        {!loading && prices.length === 0 && selectedCommodity === null && (
          <div className="text-center py-12">
            <h3 className="text-h5 text-neutral-700 mb-2">
              Select a commodity to compare
            </h3>
            <p className="text-neutral-600">
              Choose a commodity and state above to see price comparison across markets
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
