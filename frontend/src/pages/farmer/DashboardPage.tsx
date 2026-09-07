import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Bell, BriefcaseBusiness, Leaf, MapPinned, ShieldCheck, TrendingUp, Wallet } from 'lucide-react';
import { lotAPI, type FarmerLot } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

const metrics = [
  { label: 'Market readiness', value: '74%', detail: '+12% vs last week', tone: 'emerald' },
  { label: 'Best net realization', value: '₹28,740', detail: 'Madanapalle → Kurnool', tone: 'amber' },
  { label: 'Open buyer demand', value: '12', detail: 'Across 4 crop segments', tone: 'violet' },
  { label: 'Risk exposure', value: 'Low', detail: 'Weather stable, transport on time', tone: 'blue' },
];

const actions = [
  { title: 'Evaluate lot', text: 'Run the feasibility engine against market and buyer constraints.', href: '/sell', icon: Leaf },
  { title: 'Find markets', text: 'Compare mandis, costs, and expected realizations in one view.', href: '/markets', icon: MapPinned },
  { title: 'Buyer matching', text: 'See who can actually accept this lot and at what terms.', href: '/buyers', icon: BriefcaseBusiness },
];

export default function DashboardPage() {
  const toast = useToast();
  const [lot, setLot] = useState<FarmerLot | null>(null);

  useEffect(() => {
    lotAPI.listLots()
      .then((result) => setLot(result.items[0] || null))
      .catch((error: Error) => toast.error(error.message || 'Unable to load your lots'));
  }, [toast]);

  return (
    <div className="min-h-screen bg-[#080b14] text-slate-100">
      <div className="mx-auto max-w-7xl px-5 py-6 sm:px-8 lg:px-10">
        <header className="mb-8 flex flex-col gap-4 rounded-2xl border border-white/10 bg-[#0d1020]/80 p-4 backdrop-blur md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#5b4bdb] to-[#a26af5] font-bold text-white">K</div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">KrishiX</p>
              <h1 className="text-lg font-semibold text-white">Farmer portal</h1>
            </div>
          </div>
          <nav className="flex flex-wrap items-center gap-2 text-sm text-slate-300">
            <Link to="/dashboard" className="rounded-full bg-white/5 px-3 py-1.5 text-white">Dashboard</Link>
            <Link to="/sell" className="rounded-full px-3 py-1.5 hover:bg-white/5">Sell</Link>
            <Link to="/markets" className="rounded-full px-3 py-1.5 hover:bg-white/5">Markets</Link>
            <Link to="/buyers" className="rounded-full px-3 py-1.5 hover:bg-white/5">Buyers</Link>
            <Link to="/profile" className="rounded-full px-3 py-1.5 hover:bg-white/5">Profile</Link>
            <button className="ml-2 rounded-full border border-white/10 p-2 hover:bg-white/5" aria-label="Notifications">
              <Bell className="h-4 w-4" />
            </button>
          </nav>
        </header>

        <section className="mb-8 grid gap-4 lg:grid-cols-[1.6fr_0.9fr]">
          <div className="rounded-3xl border border-[#5b4bdb]/30 bg-gradient-to-br from-[#15182a] via-[#1b1f3a] to-[#0d1020] p-6 shadow-2xl shadow-[#5b4bdb]/10">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Opportunity overview</p>
                <h2 className="mt-2 text-3xl font-semibold text-white">Can this lot sell today?</h2>
              </div>
              <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">{lot ? lot.status : 'No lot yet'}</div>
            </div>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-slate-400">Commodity</p>
                <p className="mt-3 text-xl font-semibold text-white">{lot?.commodity_name || 'Create a lot'}</p>
                <p className="mt-1 text-sm text-slate-300">{lot ? `${lot.quality_grade || 'Grade not set'} · ${lot.quantity_kg || lot.quantity * 100} kg` : 'Add produce to evaluate a sale'}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-slate-400">Best realization</p>
                <p className="mt-3 text-xl font-semibold text-white">—</p>
                <p className="mt-1 text-sm text-slate-300">Run an analysis to calculate</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                <p className="text-xs uppercase tracking-[0.14em] text-slate-400">Payment window</p>
                <p className="mt-3 text-xl font-semibold text-white">{lot ? `${lot.max_payment_days} days` : '—'}</p>
                <p className="mt-1 text-sm text-slate-300">{lot ? 'Farmer requirement' : 'Not configured'}</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-[#101827] p-6">
            <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">Recommendation</p>
            <div className="mt-4 flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-500/15 text-emerald-300">
                <ShieldCheck className="h-6 w-6" />
              </div>
              <div>
                <p className="text-lg font-semibold text-white">{lot ? 'Analyze this lot' : 'Start with your lot'}</p>
                <p className="text-sm text-slate-400">{lot ? 'Compare executable buyer and market options' : 'KrishiX needs your produce details first'}</p>
              </div>
            </div>
            <div className="mt-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-100">
              {lot ? 'Your saved lot is ready for a fresh feasibility analysis using current market and buyer data.' : 'Create your first lot to see constraints, recovery options, and the best executable fallback.'}
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="rounded-2xl border border-white/10 bg-[#0f172a] p-5">
              <p className="text-sm text-slate-400">{metric.label}</p>
              <div className="mt-3 flex items-end justify-between gap-3">
                <div>
                  <p className="text-2xl font-semibold text-white">{metric.value}</p>
                  <p className="mt-1 text-xs text-slate-400">{metric.detail}</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-white/5" />
              </div>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-4 xl:grid-cols-3">
          {actions.map(({ title, text, href, icon: Icon }) => (
            <Link key={title} to={href} className="rounded-3xl border border-white/10 bg-[#0d1020] p-5 transition hover:border-violet-400/40 hover:bg-[#121a2c]">
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="text-xl font-semibold text-white">{title}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-300">{text}</p>
              <div className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-violet-300">
                Open <ArrowRight className="h-4 w-4" />
              </div>
            </Link>
          ))}
        </section>

        <section className="mt-8 rounded-3xl border border-white/10 bg-[#0d1020] p-5">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Market pulse</p>
              <h3 className="mt-2 text-xl font-semibold text-white">Price trend for the week</h3>
            </div>
            <div className="flex items-center gap-2 text-emerald-300">
              <TrendingUp className="h-4 w-4" />
              <span className="text-sm font-medium">+4.8%</span>
            </div>
          </div>
          <div className="grid h-32 grid-cols-7 gap-2">
            {[42, 48, 53, 58, 62, 66, 72].map((height, i) => (
              <div key={i} className="flex items-end justify-center">
                <div className="w-full rounded-t-xl bg-gradient-to-t from-[#5b4bdb] to-[#8ee8d2]" style={{ height: `${height}%` }} />
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
