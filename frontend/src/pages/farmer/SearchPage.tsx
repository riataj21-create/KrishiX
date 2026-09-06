import React from 'react';
import { Search, MapPinned, TrendingUp } from 'lucide-react';

const markets = [
  { name: 'Madanapalle Mandi', state: 'Andhra Pradesh', price: '₹2,700 / q', net: '₹25,900', distance: '18 km' },
  { name: 'Kurnool Market', state: 'Andhra Pradesh', price: '₹2,880 / q', net: '₹28,740', distance: '40 km' },
  { name: 'Anantapur Aggregator', state: 'Andhra Pradesh', price: '₹2,540 / q', net: '₹24,600', distance: '24 km' },
];

export default function SearchPage() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex flex-col gap-4 rounded-3xl border border-white/10 bg-[#101827] p-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Discover</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Market search</h1>
          </div>
          <div className="flex w-full max-w-md items-center gap-3 rounded-2xl border border-white/10 bg-[#0d1020] px-3 py-2">
            <Search className="h-4 w-4 text-slate-400" />
            <input className="w-full bg-transparent text-sm text-white placeholder:text-slate-500 focus:outline-none" value="Tomato, Andhra Pradesh" readOnly />
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {markets.map((market) => (
            <div key={market.name} className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
              <div className="mb-4 flex items-center justify-between">
                <p className="text-lg font-semibold text-white">{market.name}</p>
                <span className="rounded-full bg-violet-500/10 px-2 py-1 text-xs text-violet-300">Live</span>
              </div>
              <div className="space-y-3 text-sm text-slate-300">
                <div className="flex items-center justify-between"><span className="flex items-center gap-2"><MapPinned className="h-4 w-4 text-slate-400" /> {market.state}</span><span>{market.distance}</span></div>
                <div className="flex items-center justify-between"><span className="flex items-center gap-2"><TrendingUp className="h-4 w-4 text-emerald-400" /> Modal price</span><span>{market.price}</span></div>
                <div className="flex items-center justify-between"><span>Estimated net</span><span className="font-medium text-white">{market.net}</span></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
