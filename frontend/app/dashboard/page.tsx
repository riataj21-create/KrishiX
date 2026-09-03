"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowUpRight, BarChart3, CalendarDays, ChevronRight, Loader2, MapPin, RefreshCw, Search, TrendingUp } from "lucide-react";
import Link from "next/link";
import PriceCard from "@/components/PriceCard";
import { commodityAPI, farmerProfileAPI, priceAPI } from "@/lib/api";

type Price = {
  id: string;
  commodity_name: string;
  market_name: string;
  modal_price: number;
  min_price: number;
  max_price: number;
  last_updated: string;
};

const states = ["Punjab", "Maharashtra", "Haryana", "Uttar Pradesh", "Karnataka"];

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

function todayLabel() {
  return new Date().toLocaleDateString("en-IN", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  });
}

export default function DashboardPage() {
  const router = useRouter();
  const [state, setState] = useState("Punjab");
  const [district, setDistrict] = useState("");
  const [prices, setPrices] = useState<Price[]>([]);
  const [commodities, setCommodities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");
  const [userName, setUserName] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("access_token")) router.push("/auth/login");
  }, [router]);

  // Load profile for personalised greeting
  useEffect(() => {
    farmerProfileAPI.getProfile().then((p: any) => {
      if (p?.full_name) setUserName(p.full_name.split(" ")[0]);
      if (p?.state) setState(p.state);
      if (p?.district) setDistrict(p.district);
    }).catch(() => {});
  }, []);

  useEffect(() => { loadDashboard(); }, []);

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");
      const [commodityResponse, priceResponse] = await Promise.all([
        commodityAPI.listCommodities(undefined, 12),
        priceAPI.getLatestPrices({ state, district: district || undefined, limit: 6 }),
      ]);
      setCommodities(commodityResponse.items || []);
      setPrices(priceResponse.items || []);
      setLastUpdated(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    } catch {
      setError("We could not load the latest available market data.");
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(event: React.FormEvent) {
    event.preventDefault();
    loadDashboard();
  }

  const headlinePrice = prices[0];

  return (
    <div className="min-h-screen">
      <div className="page-container">
        <header className="mb-7 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <p className="mb-2 text-sm font-medium text-[var(--accent)]">{todayLabel()}</p>
            <h1 className="text-h3">{greeting()}{userName ? `, ${userName}` : ""}</h1>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">Your market view for {district || state}</p>
          </div>
          <button onClick={loadDashboard} className="btn-ghost self-start sm:self-auto" disabled={loading}>
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} /> Refresh data
          </button>
        </header>

        <section className="card mb-7 bg-white">
          <div className="card-body">
            <div className="mb-5 flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
              <div><h2 className="text-h5">Choose your market view</h2><p className="text-body-sm text-[var(--text-secondary)]">Find the latest available prices near you.</p></div>
              <span className="badge-warning"><CalendarDays size={13} className="mr-1.5" /> Updated periodically</span>
            </div>
            <form onSubmit={handleSearch} className="grid gap-3 md:grid-cols-[1fr_1fr_auto]">
              <label className="block"><span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">State</span><select className="input" value={state} onChange={(event) => setState(event.target.value)}>{states.map((item) => <option key={item}>{item}</option>)}</select></label>
              <label className="block"><span className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">District or town</span><input className="input" value={district} onChange={(event) => setDistrict(event.target.value)} placeholder="For example, Ludhiana" /></label>
              <button type="submit" className="btn-primary self-end" disabled={loading}><Search size={16} /> Search markets</button>
            </form>
            <p className="mt-4 text-xs text-[var(--text-muted)]"><MapPin size={13} className="mr-1 inline" /> Prices are sourced from available market reports. This is not live data.</p>
          </div>
        </section>

        {error && <div role="alert" className="mb-6 rounded-md border border-[#e8caca] bg-[#fbefef] px-4 py-3 text-sm text-[var(--error)]">{error}</div>}

        <section className="mb-7 grid gap-5 lg:grid-cols-[1.45fr_1fr]">
          <div className="card bg-[var(--accent)] text-white">
            <div className="card-body">
              <div className="flex items-start justify-between gap-4"><div><p className="text-sm text-white/70">Market snapshot</p><h2 className="mt-1 text-2xl font-semibold">{headlinePrice ? headlinePrice.commodity_name : "Your market overview"}</h2><p className="mt-1 text-sm text-white/70">{headlinePrice?.market_name || "Select a location to begin"}</p></div><TrendingUp size={21} className="text-[#c8e4d6]" /></div>
              {headlinePrice && <div className="mt-8 flex items-end justify-between gap-4"><div><p className="text-xs uppercase tracking-wide text-white/65">Modal price</p><p className="mt-1 text-4xl font-semibold tracking-tight">₹{headlinePrice.modal_price.toLocaleString()}<span className="ml-1 text-base font-normal text-white/70">/ quintal</span></p></div><span className="rounded-full bg-white/12 px-3 py-1.5 text-sm text-[#d9eee3]">Latest available</span></div>}
              <div className="mt-8 border-t border-white/15 pt-4 text-xs text-white/65">Last updated {lastUpdated || "when data is available"} · Source: market report</div>
            </div>
          </div>
          <div className="card"><div className="card-header flex items-center justify-between"><div><h2 className="text-h5">Decision support</h2><p className="mt-1 text-xs text-[var(--text-secondary)]">Useful next steps</p></div><BarChart3 size={18} className="text-[var(--text-muted)]" /></div><div className="divide-y divide-[var(--border)]">{[{ href: "/comparison", label: "Compare nearby markets", detail: "Review price, distance and freshness" }, { href: "/trends", label: "Review price trends", detail: "Understand recent movement" }, { href: "/saved", label: "Open saved items", detail: "Return to markets you follow" }].map((item) => <Link key={item.href} href={item.href} className="flex items-center justify-between px-5 py-4 transition-colors hover:bg-[var(--surface-subtle)]"><span><span className="block text-sm font-medium">{item.label}</span><span className="mt-1 block text-xs text-[var(--text-secondary)]">{item.detail}</span></span><ChevronRight size={16} className="text-[var(--text-muted)]" /></Link>)}</div></div>
        </section>

        <section className="mb-7">
          <div className="mb-4 flex items-end justify-between"><div><h2 className="text-h4">Commodity prices</h2><p className="mt-1 text-sm text-[var(--text-secondary)]">Latest available reports in {state}{district && `, ${district}`}</p></div><Link href="/search" className="hidden items-center gap-1 text-sm font-medium text-[var(--accent)] sm:flex">View all markets <ArrowUpRight size={15} /></Link></div>
          {loading ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{[1, 2, 3].map((item) => <div key={item} className="card h-56 shimmer" />)}</div> : prices.length ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{prices.map((price) => <PriceCard key={price.id} commodityName={price.commodity_name} marketName={price.market_name} price={price.modal_price || price.max_price} minPrice={price.min_price} maxPrice={price.max_price} lastUpdated={new Date(price.last_updated).toLocaleString()} />)}</div> : <div className="card px-5 py-12 text-center"><p className="font-medium">No market reports found</p><p className="mt-1 text-sm text-[var(--text-secondary)]">Try another state or district.</p></div>}
        </section>

        <section className="grid gap-5 lg:grid-cols-[1fr_1fr]">
          <div className="card"><div className="card-header flex items-center justify-between"><div><h2 className="text-h5">Followed commodities</h2><p className="mt-1 text-xs text-[var(--text-secondary)]">Your watchlist at a glance</p></div><Link href="/saved" className="text-xs font-medium text-[var(--accent)]">Manage</Link></div><div className="card-body flex flex-wrap gap-2">{commodities.slice(0, 6).map((commodity) => <span className="badge-primary" key={commodity.id}>{commodity.name}</span>)}{!commodities.length && <p className="text-sm text-[var(--text-secondary)]">Your saved commodities will appear here.</p>}</div></div>
          <div className="card"><div className="card-header"><h2 className="text-h5">Data note</h2></div><div className="card-body"><p className="text-sm leading-6 text-[var(--text-secondary)]">KrishiX presents the latest available reports from configured market sources. Prices are indicative and should be checked with the market before transporting produce.</p></div></div>
        </section>
      </div>
    </div>
  );
}
