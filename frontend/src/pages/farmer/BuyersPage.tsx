import React, { useEffect, useState } from 'react';
import { ArrowRight, BriefcaseBusiness, Loader2, Users } from 'lucide-react';
import { buyerAPI, type Buyer } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

export default function BuyersPage() {
  const toast = useToast();
  const [buyers, setBuyers] = useState<Buyer[]>([]);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    buyerAPI.listBuyers(undefined, 'Andhra Pradesh')
      .then((result) => {
        setBuyers(result.items);
        setStatus(result.empty_state_message || result.data_note || `Data status: ${result.data_status || 'UNKNOWN'}`);
      })
      .catch((error: Error) => toast.error(error.message || 'Unable to load buyers'))
      .finally(() => setLoading(false));
  }, [toast]);

  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-[#101827] p-6">
        <div className="mb-6 flex items-center justify-between"><div><p className="text-xs uppercase tracking-[0.18em] text-violet-300">Buyers</p><h1 className="mt-2 text-3xl font-semibold text-white">Buyer discovery</h1></div><div className="rounded-full border border-white/10 bg-black/10 p-2 text-slate-300"><Users className="h-4 w-4" /></div></div>
        {loading ? <div className="flex items-center justify-center p-12 text-slate-300"><Loader2 className="mr-2 h-5 w-5 animate-spin" /> Loading buyer matches...</div> : buyers.length === 0 ? <div className="rounded-2xl border border-dashed border-white/15 p-8 text-center text-slate-400">{status || 'No active buyers currently match this listing.'}</div> : <div className="space-y-4">{buyers.map((buyer) => <div key={buyer.id} className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-[#0d1020] p-5 md:flex-row md:items-center md:justify-between"><div className="flex items-center gap-4"><div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300"><BriefcaseBusiness className="h-5 w-5" /></div><div><p className="text-lg font-semibold text-white">{buyer.name}</p><p className="text-sm text-slate-300">{buyer.buyer_type || 'Buyer'} · {buyer.commodity_name || 'Multiple commodities'} · {buyer.district || buyer.state || 'Location not specified'}</p><p className="mt-1 text-xs text-slate-500">{buyer.is_verified ? 'Verified' : 'Reference/demo'}{buyer.rating ? ` · ${buyer.rating.toFixed(1)}/5 rating` : ''}</p></div></div><div className="flex flex-wrap items-center gap-4 text-sm text-slate-300"><span>{buyer.quality_grade || 'Quality terms vary'}</span><span>{buyer.payment_terms || 'Payment terms available on offer'}</span>{buyer.whatsapp_link && <a href={buyer.whatsapp_link} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 rounded-full border border-violet-400/30 bg-violet-500/10 px-3 py-1.5 text-violet-200">Contact <ArrowRight className="h-4 w-4" /></a>}</div></div>)}</div>}
        {status && buyers.length > 0 && <p className="mt-5 text-xs leading-5 text-slate-500">{status}</p>}
      </div>
    </div>
  );
}
