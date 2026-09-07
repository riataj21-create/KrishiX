import React from 'react';
import { Activity, TrendingUp } from 'lucide-react';

const data = [24, 31, 30, 38, 42, 49, 52, 59, 60, 64, 68, 71];

export default function TrendsPage() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-[#101827] p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Signals</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Trend intelligence</h1>
          </div>
          <div className="flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-sm text-emerald-300">
            <TrendingUp className="h-4 w-4" /> +4.8%
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
            <div className="mb-5 flex items-center gap-2 text-slate-300"><Activity className="h-4 w-4 text-cyan-300" /> Weekly price movement</div>
            <div className="flex h-56 items-end gap-2">
              {data.map((value, index) => (
                <div key={index} className="flex flex-1 items-end justify-center">
                  <div className="w-full rounded-t-xl bg-gradient-to-t from-[#5b4bdb] via-violet-500 to-cyan-300" style={{ height: `${value}%` }} />
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Recommendation</p>
              <p className="mt-3 text-xl font-semibold text-white">SELL NOW</p>
              <p className="mt-2 text-sm text-slate-300">Price trend is stable, transport costs are manageable, and the window remains favourable.</p>
            </div>
            <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Risk note</p>
              <p className="mt-3 text-sm text-slate-300">Weather risk remains moderate, but not severe enough to offset the current spread.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
