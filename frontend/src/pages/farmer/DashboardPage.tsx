import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Bell, BriefcaseBusiness, Leaf, MapPinned, ShieldCheck, TrendingUp } from 'lucide-react';
import { lotAPI, type FarmerLot } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

const metrics = [
  { label: 'Market readiness', value: '74%', detail: '+12% vs last week', tone: 'text-[#89d5ba]' },
  { label: 'Best net realization', value: '₹28,740', detail: 'Madanapalle → Kurnool', tone: 'text-[#f0bf64]' },
  { label: 'Open buyer demand', value: '12', detail: 'Across 4 crop segments', tone: 'text-[#c6c0ff]' },
  { label: 'Risk exposure', value: 'Low', detail: 'Weather stable, transport on time', tone: 'text-[#9bd6ed]' },
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
    <div className="min-h-screen bg-[#080b14] text-[#f5f1e8]">
      <div className="mx-auto max-w-[1440px] px-5 py-8 sm:px-8 lg:px-10">
        <header className="mb-10 flex items-start justify-between border-b border-white/[0.08] pb-7">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#f0bf64]">Farmer intelligence brief · 07 Sep 2026</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-[#e0e2ef] sm:text-5xl">Know where your harvest belongs.</h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-[#c8c4d7]">A clear view of executable markets, buyer demand, and the constraints that shape your next sale.</p>
          </div>
          <button className="rounded-lg border border-white/10 bg-[#181b25] p-2.5 text-[#c8c4d7] transition hover:border-[#c6c0ff]/50 hover:text-white" aria-label="Notifications">
            <Bell className="h-4 w-4" />
          </button>
        </header>

        <section className="mb-8 grid gap-5 lg:grid-cols-[1.55fr_0.85fr]">
          <div className="glass-panel bg-gradient-to-br from-[#30275a]/80 via-[#15182a]/80 to-[#0d1020]/80 p-6 shadow-[#5b4bdb]/20 sm:p-8">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#c6c0ff]">Best current opportunity</p>
                <h2 className="mt-3 text-3xl font-semibold text-white">Can this lot sell today?</h2>
              </div>
              <span className="rounded-full border border-white/15 bg-black/20 px-3 py-1 text-[11px] uppercase tracking-wider text-[#c8c4d7]">{lot?.status || 'Awaiting lot'}</span>
            </div>
            <div className="mt-8 grid gap-3 md:grid-cols-3">
              <InfoCell label="Commodity" value={lot?.commodity_name || 'Create a lot'} detail={lot ? `${lot.quality_grade || 'Grade not set'} · ${lot.quantity_kg || lot.quantity * 100} kg` : 'Add produce to evaluate a sale'} />
              <InfoCell label="Best realization" value="—" detail="Run an analysis to calculate" />
              <InfoCell label="Payment window" value={lot ? `${lot.max_payment_days} days` : '—'} detail={lot ? 'Farmer requirement' : 'Not configured'} />
            </div>
            <Link to="/sell" className="mt-7 inline-flex items-center gap-2 rounded-lg bg-[#5b4bdb] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#6c5de5]">
              Analyze selling options <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="glass-panel p-6">
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#89d5ba]">Decision signal</p>
            <div className="mt-5 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-[#1d6f59]/30 text-[#89d5ba]"><ShieldCheck className="h-5 w-5" /></div>
              <div>
                <p className="font-serif text-xl font-semibold text-white">{lot ? 'Lot ready for analysis' : 'Start with your lot'}</p>
                <p className="mt-1 text-xs text-[#928fa0]">{lot ? 'Compare executable buyer and market options' : 'Add produce details to begin'}</p>
              </div>
            </div>
            <div className="mt-7 border-t border-white/[0.08] pt-5 text-sm leading-6 text-[#c8c4d7]">
              {lot ? 'Your saved lot is ready for a fresh feasibility analysis using current market and buyer data.' : 'Create your first lot to see constraints, recovery options, and the best executable fallback.'}
            </div>
          </div>
        </section>

        <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="glass-panel p-5">
              <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#928fa0]">{metric.label}</p>
              <p className={`mt-4 font-serif text-3xl font-semibold ${metric.tone}`}>{metric.value}</p>
              <p className="mt-2 text-xs text-[#928fa0]">{metric.detail}</p>
            </div>
          ))}
        </section>

        <section className="mt-10">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#f0bf64]">Operations</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Move from signal to action</h2>
            </div>
            <Link to="/opportunities" className="hidden items-center gap-2 text-xs font-semibold text-[#c6c0ff] sm:inline-flex">View all <ArrowRight className="h-3.5 w-3.5" /></Link>
          </div>
          <div className="grid gap-3 xl:grid-cols-3">
            {actions.map(({ title, text, href, icon: Icon }) => (
              <Link key={title} to={href} className="glass-panel group p-5 transition hover:-translate-y-0.5">
                <div className="mb-5 flex h-10 w-10 items-center justify-center rounded-lg bg-[#27234d] text-[#c6c0ff]"><Icon className="h-5 w-5" /></div>
                <h3 className="font-serif text-xl font-semibold text-white">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-[#c8c4d7]">{text}</p>
                <div className="mt-5 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#c6c0ff]">Open <ArrowRight className="h-3.5 w-3.5 transition group-hover:translate-x-1" /></div>
              </Link>
            ))}
          </div>
        </section>

        <section className="glass-panel mt-10 p-5 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#928fa0]">Market pulse</p>
              <h2 className="mt-2 text-2xl font-semibold text-white">Price movement, last seven days</h2>
            </div>
            <div className="flex items-center gap-2 text-[#89d5ba]"><TrendingUp className="h-4 w-4" /><span className="text-sm font-semibold">+4.8%</span></div>
          </div>
          <div className="mt-7 grid h-32 grid-cols-7 items-end gap-2">
            {[42, 48, 53, 58, 62, 66, 72].map((height, index) => <div key={index} className="h-full rounded-t bg-gradient-to-t from-[#5b4bdb] to-[#89d5ba]" style={{ height: `${height}%` }} />)}
          </div>
          <div className="mt-3 flex justify-between text-[10px] uppercase tracking-wider text-[#928fa0]"><span>01 Sep</span><span>07 Sep</span></div>
        </section>
      </div>
    </div>
  );
}

function InfoCell({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-4 backdrop-blur-md">
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#928fa0]">{label}</p>
      <p className="mt-3 font-serif text-xl font-semibold text-white">{value}</p>
      <p className="mt-1 text-xs text-[#c8c4d7]">{detail}</p>
    </div>
  );
}
