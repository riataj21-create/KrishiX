"use client";

import { FormEvent, useEffect, useState } from "react";
import { AlertCircle, Loader2, Search as SearchIcon } from "lucide-react";
import { priceAPI, savedAPI } from "@/lib/api";
import PriceCard from "@/components/PriceCard";

export default function SearchPage() {
  const [state, setState] = useState("Punjab");
  const [district, setDistrict] = useState("");
  const [query, setQuery] = useState("");
  const [prices, setPrices] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());

  // Load already-saved commodity ids so cards render the right icon state
  useEffect(() => {
    savedAPI.getSavedCommodities(100, 0)
      .then((res: any) => {
        const ids = (res.items || []).map((item: any) => item.commodity_id as string);
        setSavedIds(new Set(ids));
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      if (query.trim()) search();
    }, 350);
    return () => window.clearTimeout(timer);
  }, [query]);

  async function search(event?: FormEvent) {
    event?.preventDefault();
    try {
      setLoading(true);
      setError("");
      const response = await priceAPI.getLatestPrices({
        state,
        district: district || undefined,
        limit: 24,
      });
      const filtered = query.trim()
        ? response.items.filter(
            (item: any) =>
              item.commodity_name.toLowerCase().includes(query.trim().toLowerCase()) ||
              item.market_name.toLowerCase().includes(query.trim().toLowerCase())
          )
        : response.items;
      setPrices(filtered || []);
    } catch {
      setError("We could not load market reports. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(commodityId: string) {
    try {
      await savedAPI.saveCommodity(commodityId);
      setSavedIds((prev) => new Set([...prev, commodityId]));
    } catch {
      // silently fail — e.g. already saved (409)
    }
  }

  async function handleUnsave(commodityId: string) {
    try {
      await savedAPI.unsaveCommodity(commodityId);
      setSavedIds((prev) => {
        const next = new Set(prev);
        next.delete(commodityId);
        return next;
      });
    } catch {}
  }

  return (
    <div className="page-container">
      <header className="mb-7">
        <p className="mb-2 text-sm font-medium text-[var(--accent)]">Market directory</p>
        <h1 className="text-h3">Find a market report</h1>
        <p className="mt-1 text-sm text-[var(--text-secondary)]">
          Search structured price data by commodity, location or market.
        </p>
      </header>

      <section className="card mb-7">
        <div className="card-body">
          <form onSubmit={search} className="grid gap-3 md:grid-cols-[1.3fr_1fr_1fr_auto]">
            <label className="relative block md:col-span-1">
              <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                Commodity or market
              </span>
              <SearchIcon size={16} className="absolute left-3 top-[37px] text-[var(--text-muted)]" />
              <input
                className="input pl-9"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search tomato, Ludhiana..."
              />
            </label>
            <label>
              <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                State
              </span>
              <select className="input" value={state} onChange={(e) => setState(e.target.value)}>
                <option>Punjab</option>
                <option>Maharashtra</option>
                <option>Haryana</option>
                <option>Uttar Pradesh</option>
                <option>Karnataka</option>
              </select>
            </label>
            <label>
              <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                District
              </span>
              <input
                className="input"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                placeholder="Optional"
              />
            </label>
            <button className="btn-primary self-end" type="submit" disabled={loading}>
              {loading ? <Loader2 size={16} className="animate-spin" /> : <SearchIcon size={16} />}
              Search
            </button>
          </form>
          <p className="mt-4 text-xs text-[var(--text-muted)]">
            Search is handled through FastAPI and PostgreSQL. No AI service is used for retrieval.
          </p>
        </div>
      </section>

      {error && (
        <div role="alert" className="mb-6 flex gap-2 rounded-md border border-[#e8caca] bg-[#fbefef] px-4 py-3 text-sm text-[var(--error)]">
          <AlertCircle size={17} />
          {error}
        </div>
      )}

      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-h5">Latest available reports</h2>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">
            {prices.length} results · {state}{district && `, ${district}`}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map((i) => <div key={i} className="card h-56 shimmer" />)}
        </div>
      ) : prices.length ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {prices.map((price) => (
            <PriceCard
              key={price.id}
              commodityName={price.commodity_name}
              marketName={price.market_name}
              price={price.modal_price || price.max_price}
              minPrice={price.min_price}
              maxPrice={price.max_price}
              lastUpdated={new Date(price.last_updated).toLocaleString()}
              commodityId={price.commodity_id}
              saved={savedIds.has(price.commodity_id)}
              onSave={handleSave}
              onUnsave={handleUnsave}
            />
          ))}
        </div>
      ) : (
        <div className="card px-5 py-12 text-center">
          <p className="font-medium">No matching reports</p>
          <p className="mt-1 text-sm text-[var(--text-secondary)]">Try a different commodity or location.</p>
        </div>
      )}
    </div>
  );
}
