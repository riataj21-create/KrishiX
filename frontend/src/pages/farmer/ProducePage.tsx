import React, { useEffect, useState } from 'react';
import { ArrowRight, Loader2, PackagePlus } from 'lucide-react';
import { Link } from 'react-router-dom';
import { lotAPI, type FarmerLot } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

export default function ProducePage() {
  const toast = useToast();
  const [lots, setLots] = useState<FarmerLot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    lotAPI.listLots().then((result) => setLots(result.items)).catch((error: Error) => toast.error(error.message || 'Unable to load produce')).finally(() => setLoading(false));
  }, [toast]);

  return <Page title="My produce" copy="Manage your current lots and see where each one can realistically sell.">
    {loading ? <Loading /> : lots.length === 0 ? <Empty /> : <div className="grid gap-5 md:grid-cols-2">{lots.map((lot) => <article key={lot.id} className="photo-hero min-h-[330px] bg-[url('https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=1200&q=80')] p-6"><div className="photo-content flex h-full flex-col justify-end"><div className="flex items-start justify-between gap-3"><div><p className="eyebrow">Current harvest</p><p className="mt-2 font-serif text-3xl font-semibold text-[#f5f1e8]">{lot.commodity_name || 'Produce lot'}</p><p className="mt-1 text-sm text-[#c8c4d7]">{lot.quality_grade || 'Quality not specified'} · {lot.quantity_kg || lot.quantity * 100} kg</p></div><span className="rounded-full border border-white/20 bg-black/20 px-2.5 py-1 text-xs text-[#f5f1e8]">{lot.status}</span></div><div className="mt-6 grid grid-cols-2 gap-3 border-t border-white/15 pt-4 text-sm"><div><p className="text-[#a9a8b3]">Location</p><p className="mt-1 text-[#f5f1e8]">{lot.district}, {lot.state}</p></div><div><p className="text-[#a9a8b3]">Sell by</p><p className="mt-1 text-[#f5f1e8]">{lot.sell_by}</p></div></div><Link to={`/opportunities/${lot.id}`} className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-[#d6a84f]">Analyze <ArrowRight className="h-4 w-4" /></Link></div></article>)}</div>}
  </Page>;
}

function Page({ title, copy, children }: { title: string; copy: string; children: React.ReactNode }) {
  return <div className="page-container min-h-screen"><div className="mb-8 flex flex-col gap-4 border-b border-white/10 pb-6 sm:flex-row sm:items-end sm:justify-between"><div><p className="eyebrow">KrishiX / portfolio</p><h1 className="editorial-title mt-2">{title}</h1><p className="mt-2 max-w-xl text-sm leading-6 text-[#a9a8b3]">{copy}</p></div><Link to="/sell" className="btn-primary self-start"><PackagePlus className="h-4 w-4" /> Add produce</Link></div>{children}</div>;
}
function Loading() { return <div className="glass-panel flex items-center gap-2 p-8 text-sm text-[#a9a8b3]"><Loader2 className="h-4 w-4 animate-spin" /> Loading your lots...</div>; }
function Empty() { return <div className="glass-panel p-10 text-center"><p className="font-serif text-xl font-medium">No produce yet</p><p className="mt-2 text-sm text-[#a9a8b3]">Add your first lot to start comparing selling opportunities.</p><Link to="/sell" className="btn-primary mt-5">Add produce</Link></div>; }
