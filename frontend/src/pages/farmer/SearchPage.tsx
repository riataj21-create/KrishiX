import React, { useEffect, useState } from 'react';
import { Loader2, MapPinned, Search, TrendingUp } from 'lucide-react';
import { commodityAPI, marketAPI, priceAPI, type Commodity, type Market } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

type MarketResult = Market & { modal_price?: number | null; estimated_net_realization?: number | null; data_freshness?: string };

export default function SearchPage() {
  const toast = useToast();
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<MarketResult[]>([]);
  const [selectedCommodity, setSelectedCommodity] = useState('');
  const [state, setState] = useState('Andhra Pradesh');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    commodityAPI.listCommodities(undefined, 100)
      .then((result) => {
        setCommodities(result.items);
        if (result.items[0]) setSelectedCommodity(result.items[0].id);
      })
      .catch((error: Error) => toast.error(error.message || 'Unable to load commodities'));
  }, [toast]);

  useEffect(() => {
    if (!selectedCommodity) return;
    setLoading(true);
    Promise.all([
      marketAPI.listMarkets(state, undefined, 100),
      priceAPI.getLatestPrices({ state, commodity_id: selectedCommodity, limit: 100 }),
    ])
      .then(([marketResult, priceResult]) => {
        const prices = new Map(priceResult.items.map((price: any) => [price.market_id, price]));
        setMarkets(marketResult.items.map((market) => {
          const price = prices.get(market.id) as any;
          return { ...market, modal_price: price?.modal_price, data_freshness: price?.data_freshness };
        }).filter((market) => market.modal_price != null));
      })
      .catch((error: Error) => toast.error(error.message || 'Unable to load market prices'))
      .finally(() => setLoading(false));
  }, [selectedCommodity, state, toast]);

  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex flex-col gap-4 rounded-3xl border border-white/10 bg-[#101827] p-5 md:flex-row md:items-center md:justify-between">
          <div><p className="text-xs uppercase tracking-[0.18em] text-violet-300">Discover</p><h1 className="mt-2 text-3xl font-semibold text-white">Market search</h1></div>
          <div className="flex w-full max-w-md items-center gap-3 rounded-2xl border border-white/10 bg-[#0d1020] px-3 py-2">
            <Search className="h-4 w-4 text-slate-400" />
            <select className="w-full bg-transparent text-sm text-white outline-none" value={selectedCommodity} onChange={(event) => setSelectedCommodity(event.target.value)}>
              {commodities.map((commodity) => <option className="bg-[#0d1020]" key={commodity.id} value={commodity.id}>{commodity.name}</option>)}
            </select>
          </div>
        </div>

        <div className="mb-5 flex items-center gap-3">
          <label className="text-sm text-slate-400" htmlFor="state">State</label>
          <input id="state" className="rounded-xl border border-white/10 bg-[#101827] px-3 py-2 text-sm text-white outline-none focus:border-violet-400" value={state} onChange={(event) => setState(event.target.value)} />
        </div>

        {loading ? <div className="flex items-center justify-center rounded-3xl border border-white/10 bg-[#101827] p-16 text-slate-300"><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Loading latest available prices...</div> : markets.length === 0 ? <div className="rounded-3xl border border-dashed border-white/15 bg-[#101827] p-12 text-center text-slate-400">No price records found for this commodity and state.</div> : (
          <div className="grid gap-4 md:grid-cols-3">
            {markets.map((market) => (
              <div key={market.id} className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
                <div className="mb-4 flex items-center justify-between"><p className="text-lg font-semibold text-white">{market.name}</p><span className="rounded-full bg-violet-500/10 px-2 py-1 text-xs text-violet-300">{market.data_freshness || 'Available'}</span></div>
                <div className="space-y-3 text-sm text-slate-300">
                  <div className="flex items-center justify-between"><span className="flex items-center gap-2"><MapPinned className="h-4 w-4 text-slate-400" /> {market.district}</span><span>{market.market_type || 'Mandi'}</span></div>
                  <div className="flex items-center justify-between"><span className="flex items-center gap-2"><TrendingUp className="h-4 w-4 text-emerald-400" /> Modal price</span><span className="font-medium text-white">₹{market.modal_price?.toLocaleString('en-IN')} / q</span></div>
                  <p className="border-t border-white/10 pt-3 text-xs text-slate-500">Price is the latest available observation, not a guaranteed receipt.</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
