import React from 'react';
import { Bookmark, MapPinned, Star } from 'lucide-react';

const saves = [
  { name: 'Madanapalle Mandi', type: 'Market', note: 'High conversion with lower transport cost.' },
  { name: 'Tomato', type: 'Commodity', note: 'Saved for monitoring and price alerts.' },
  { name: 'Kurnool Market', type: 'Market', note: 'Strong buyer demand available this week.' },
];

export default function SavedPage() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-[#101827] p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Saved</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Saved markets & commodities</h1>
          </div>
          <div className="rounded-full border border-white/10 bg-black/10 p-2 text-slate-300"><Bookmark className="h-4 w-4" /></div>
        </div>

        <div className="space-y-4">
          {saves.map((item) => (
            <div key={item.name} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-[#0d1020] p-4">
              <div className="flex items-center gap-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
                  {item.type === 'Market' ? <MapPinned className="h-5 w-5" /> : <Star className="h-5 w-5" />}
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">{item.name}</p>
                  <p className="text-sm text-slate-300">{item.note}</p>
                </div>
              </div>
              <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-300">{item.type}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
