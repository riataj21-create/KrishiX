/**
 * Saved Markets & Commodities Page
 * Manage user's bookmarked items
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Loader2, Heart, Trash2 } from "lucide-react";
import { savedAPI } from "@/lib/api";

type Tab = "markets" | "commodities";

export default function SavedPage() {
  const router = useRouter();
  
  const [activeTab, setActiveTab] = useState<Tab>("markets");
  const [savedMarkets, setSavedMarkets] = useState<any[]>([]);
  const [savedCommodities, setSavedCommodities] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Check auth
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/auth/login");
    }
  }, [router]);

  // Load data
  useEffect(() => {
    loadSavedItems();
  }, []);

  const loadSavedItems = async () => {
    try {
      setLoading(true);
      setError("");

      const [marketsResponse, commoditiesResponse] = await Promise.all([
        savedAPI.getSavedMarkets(),
        savedAPI.getSavedCommodities(),
      ]);

      setSavedMarkets(marketsResponse.items || []);
      setSavedCommodities(commoditiesResponse.items || []);
    } catch (err: any) {
      setError("Failed to load saved items");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveMarket = async (marketId: string) => {
    try {
      await savedAPI.unsaveMarket(marketId);
      setSavedMarkets(savedMarkets.filter((m) => m.market_id !== marketId));
    } catch (err) {
      setError("Failed to remove market");
      console.error(err);
    }
  };

  const handleRemoveCommodity = async (commodityId: string) => {
    try {
      await savedAPI.unsaveCommodity(commodityId);
      setSavedCommodities(
        savedCommodities.filter((c) => c.commodity_id !== commodityId)
      );
    } catch (err) {
      setError("Failed to remove commodity");
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <section className="bg-white border-b border-neutral-200">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <h1 className="text-h3 mb-2">Saved Items</h1>
          <p className="text-neutral-600">
            Your bookmarked markets and commodities
          </p>

          {/* Tabs */}
          <div className="flex gap-4 mt-6 border-b border-neutral-200">
            <button
              onClick={() => setActiveTab("markets")}
              className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                activeTab === "markets"
                  ? "border-b-primary text-primary"
                  : "border-b-transparent text-neutral-600 hover:text-neutral-900"
              }`}
            >
              Markets ({savedMarkets.length})
            </button>
            <button
              onClick={() => setActiveTab("commodities")}
              className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                activeTab === "commodities"
                  ? "border-b-primary text-primary"
                  : "border-b-transparent text-neutral-600 hover:text-neutral-900"
              }`}
            >
              Commodities ({savedCommodities.length})
            </button>
          </div>
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
            <p className="text-neutral-600">Loading saved items...</p>
          </div>
        )}

        {/* Saved Markets Tab */}
        {!loading && activeTab === "markets" && (
          <>
            {savedMarkets.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {savedMarkets.map((market) => (
                  <div key={market.market_id} className="card group hover:shadow-lg transition-shadow">
                    <div className="card-body">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-h6 text-neutral-900">
                            {market.market_name}
                          </h3>
                          <p className="text-sm text-neutral-600 mt-1">
                            {market.state} • {market.district}
                          </p>
                        </div>
                        <Heart className="w-5 h-5 text-primary fill-current flex-shrink-0" />
                      </div>

                      <div className="flex gap-2 pt-4 border-t border-neutral-200">
                        <a
                          href={`/comparison?state=${market.state}`}
                          className="btn-sm btn-ghost flex-1 text-center"
                        >
                          Compare Prices
                        </a>
                        <button
                          onClick={() => handleRemoveMarket(market.market_id)}
                          className="btn-sm px-3 text-danger hover:bg-danger/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Heart className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
                <h3 className="text-h5 text-neutral-700 mb-2">
                  No saved markets yet
                </h3>
                <p className="text-neutral-600 mb-6">
                  Bookmark markets to quickly access their prices
                </p>
                <a href="/dashboard" className="btn-primary">
                  Find Markets
                </a>
              </div>
            )}
          </>
        )}

        {/* Saved Commodities Tab */}
        {!loading && activeTab === "commodities" && (
          <>
            {savedCommodities.length > 0 ? (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {savedCommodities.map((commodity) => (
                  <div key={commodity.commodity_id} className="card group hover:shadow-lg transition-shadow">
                    <div className="card-body">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-h6 text-neutral-900">
                            {commodity.commodity_name}
                          </h3>
                          <p className="text-sm text-neutral-600 mt-1">
                            {commodity.category}
                          </p>
                        </div>
                        <Heart className="w-5 h-5 text-primary fill-current flex-shrink-0" />
                      </div>

                      <div className="flex gap-2 pt-4 border-t border-neutral-200">
                        <a
                          href={`/comparison?commodity=${commodity.commodity_id}`}
                          className="btn-sm btn-ghost flex-1 text-center"
                        >
                          Compare Prices
                        </a>
                        <button
                          onClick={() => handleRemoveCommodity(commodity.commodity_id)}
                          className="btn-sm px-3 text-danger hover:bg-danger/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Heart className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
                <h3 className="text-h5 text-neutral-700 mb-2">
                  No saved commodities yet
                </h3>
                <p className="text-neutral-600 mb-6">
                  Bookmark commodities to track their prices
                </p>
                <a href="/dashboard" className="btn-primary">
                  Find Commodities
                </a>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}
