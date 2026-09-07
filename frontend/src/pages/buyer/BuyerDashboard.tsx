import React from 'react';
import { ArrowRight, PackageCheck, TrendingUp, Wallet } from 'lucide-react';

const cards = [
  { label: 'Demand matched', value: '18', detail: 'lots awaiting review' },
  { label: 'Win rate', value: '72%', detail: 'this month' },
  { label: 'Avg. payment', value: '4 days', detail: 'standard cycle' },
  { label: 'Reputation', value: '4.9/5', detail: 'verified partners' },
];

export default function BuyerDashboard() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 rounded-3xl border border-white/10 bg-[#101827] p-6">
          <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">Buyer portal</p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Procurement overview</h1>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {cards.map((card) => (
            <div key={card.label} className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
              <p className="text-sm text-slate-400">{card.label}</p>
              <p className="mt-3 text-3xl font-semibold text-white">{card.value}</p>
              <p className="mt-1 text-xs text-slate-400">{card.detail}</p>
            </div>
          ))}
        </div>

        <div className="mt-8 grid gap-5 lg:grid-cols-3">
          <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-emerald-500/10 p-2 text-emerald-300"><PackageCheck className="h-5 w-5" /></div>
              <p className="text-lg font-semibold text-white">Open requirements</p>
            </div>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>Tomato • Grade A • 300 kg</li>
              <li>Onion • Grade B • 500 kg</li>
              <li>Chilli • Grade A • 200 kg</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-violet-500/10 p-2 text-violet-300"><TrendingUp className="h-5 w-5" /></div>
              <p className="text-lg font-semibold text-white">Market pulse</p>
            </div>
            <div className="mt-4 h-28 rounded-2xl bg-gradient-to-r from-violet-500/10 via-cyan-500/10 to-emerald-500/10 p-4">
              <div className="flex h-full items-end gap-2">
                {[22, 30, 35, 48, 52, 64, 73].map((value, index) => (
                  <div key={index} className="flex-1 rounded-t-xl bg-gradient-to-t from-[#5b4bdb] to-cyan-300" style={{ height: `${value}%` }} />
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-amber-500/10 p-2 text-amber-300"><Wallet className="h-5 w-5" /></div>
              <p className="text-lg font-semibold text-white">Quick actions</p>
            </div>
            <div className="mt-4 space-y-3">
              <button className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-left text-sm text-slate-300">
                Review fit scores <ArrowRight className="h-4 w-4" />
              </button>
              <button className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-left text-sm text-slate-300">
                Confirm pickup slots <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
