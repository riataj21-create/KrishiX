import React, { useEffect, useState } from 'react';
import { Bookmark, Loader2, MapPinned, Star } from 'lucide-react';
import { savedAPI } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

export default function SavedPage() {
  const toast = useToast();
  const [markets, setMarkets] = useState<Array<{ id: string; market_name: string; state: string; district: string }>>([]);
  const [commodities, setCommodities] = useState<Array<{ id: string; commodity_name: string; category?: string | null }>>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([savedAPI.getSavedMarkets(), savedAPI.getSavedCommodities()])
      .then(([marketResult, commodityResult]) => { setMarkets(marketResult.items); setCommodities(commodityResult.items); })
      .catch((error: Error) => toast.error(error.message || 'Unable to load saved items'))
      .finally(() => setLoading(false));
  }, [toast]);

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

        {loading ? <div className="flex items-center gap-2 p-8 text-sm text-slate-400"><Loader2 className="h-4 w-4 animate-spin" /> Loading saved items...</div> : markets.length === 0 && commodities.length === 0 ? <div className="rounded-2xl border border-dashed border-white/15 p-10 text-center text-sm text-slate-400">Save markets you want to compare later.</div> : <div className="space-y-4">
          {markets.map((item) => (
            <div key={item.id} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-[#0d1020] p-4">
              <div className="flex items-center gap-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
                  <MapPinned className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-lg font-semibold text-white">{item.market_name}</p>
                  <p className="text-sm text-slate-300">{item.district}, {item.state}</p>
                </div>
              </div>
              <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-300">Market</span>
            </div>
          ))}
          {commodities.map((item) => <div key={item.id} className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-[#0d1020] p-4"><div className="flex items-center gap-4"><div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300"><Star className="h-5 w-5" /></div><div><p className="text-lg font-semibold text-white">{item.commodity_name}</p><p className="text-sm text-slate-300">{item.category || 'Commodity'}</p></div></div><span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs text-slate-300">Commodity</span></div>)}
        </div>}
      </div>
    </div>
  );
}
