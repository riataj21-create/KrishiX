import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, Gauge, MapPinned, ShieldAlert, Sparkles } from 'lucide-react';

const constraints = [
  { title: 'Quantity', status: 'Failing', note: 'Buyer requires 300 kg; farmer lot is 80 kg', color: 'text-rose-300' },
  { title: 'Quality', status: 'Failing', note: 'Grade B does not meet Grade A requirement', color: 'text-rose-300' },
  { title: 'Payment', status: 'Passing', note: 'Buyer payment window matches 2-day maximum', color: 'text-emerald-300' },
];

export default function DecisionPage() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center gap-3 text-sm text-slate-300">
          <Link to="/dashboard" className="inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-1.5 hover:bg-white/5">
            <ArrowLeft className="h-4 w-4" /> Back to dashboard
          </Link>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <section className="rounded-3xl border border-white/10 bg-[#101827] p-6">
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Feasibility engine</p>
            <h1 className="mt-3 text-3xl font-semibold text-white">Selling decision</h1>
            <div className="mt-6 rounded-2xl border border-rose-400/20 bg-rose-500/8 p-4">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-rose-500/10 p-2 text-rose-300"><ShieldAlert className="h-5 w-5" /></div>
                <div>
                  <p className="text-lg font-semibold text-white">Not viable today</p>
                  <p className="text-sm text-slate-300">The best buyer is blocked by quantity and quality constraints.</p>
                </div>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Decision</p>
                <p className="mt-3 text-2xl font-semibold text-white">NOT_VIABLE</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Gap</p>
                <p className="mt-3 text-2xl font-semibold text-white">220 kg</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Minimum viable change</p>
                <p className="mt-3 text-2xl font-semibold text-white">Aggregate</p>
              </div>
            </div>

            <div className="mt-6 space-y-3">
              {constraints.map(({ title, status, note, color }) => (
                <div key={title} className="flex items-start justify-between gap-3 rounded-2xl border border-white/10 bg-[#0d1020] p-4">
                  <div>
                    <p className="text-sm font-medium text-white">{title}</p>
                    <p className="mt-1 text-sm text-slate-300">{note}</p>
                  </div>
                  <span className={`rounded-full border border-white/10 px-2.5 py-1 text-xs font-medium ${color}`}>{status}</span>
                </div>
              ))}
            </div>
          </section>

          <aside className="space-y-5">
            <div className="rounded-3xl border border-white/10 bg-[#101827] p-5">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-violet-500/10 p-2 text-violet-300"><Gauge className="h-5 w-5" /></div>
                <p className="text-lg font-semibold text-white">What can change?</p>
              </div>
              <ul className="mt-4 space-y-3 text-sm text-slate-300">
                <li className="flex items-start gap-2"><CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-300" /> Aggregate 220 kg from a compatible farmer group.</li>
                <li className="flex items-start gap-2"><CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-300" /> Improve to Grade A by sorting to meet buyer spec.</li>
                <li className="flex items-start gap-2"><CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-300" /> Keep the current lot for a buyer with flexible quality windows.</li>
              </ul>
            </div>

            <div className="rounded-3xl border border-white/10 bg-[#101827] p-5">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-cyan-500/10 p-2 text-cyan-300"><Sparkles className="h-5 w-5" /></div>
                <p className="text-lg font-semibold text-white">Recovery options</p>
              </div>
              <div className="mt-4 space-y-3 text-sm text-slate-300">
                <div className="flex items-center justify-between rounded-2xl bg-black/10 p-3"><span>FPO pooling</span><span className="text-emerald-300">Feasible</span></div>
                <div className="flex items-center justify-between rounded-2xl bg-black/10 p-3"><span>Local buyer fallback</span><span className="text-violet-300">High confidence</span></div>
                <div className="flex items-center justify-between rounded-2xl bg-black/10 p-3"><span>Sell later</span><span className="text-amber-300">Monitor</span></div>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-[#101827] p-5">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-amber-500/10 p-2 text-amber-300"><MapPinned className="h-5 w-5" /></div>
                <p className="text-lg font-semibold text-white">Best executable fallback</p>
              </div>
              <p className="mt-3 text-sm text-slate-300">Sell to the nearest mandi with an accepted grade and a 2-day payment cycle.</p>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
