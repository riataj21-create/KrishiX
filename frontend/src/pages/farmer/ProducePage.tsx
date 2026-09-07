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
    {loading ? <Loading /> : lots.length === 0 ? <Empty /> : <div className="grid gap-4 md:grid-cols-2">{lots.map((lot) => <article key={lot.id} className="border border-white/10 bg-[#15182a] p-5"><div className="flex items-start justify-between gap-3"><div><p className="text-xl font-semibold">{lot.commodity_name || 'Produce lot'}</p><p className="mt-1 text-sm text-[#a9a8b3]">{lot.quality_grade || 'Quality not specified'} · {lot.quantity_kg || lot.quantity * 100} kg</p></div><span className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-[#a9a8b3]">{lot.status}</span></div><dl className="mt-5 grid grid-cols-2 gap-4 text-sm"><div><dt className="text-[#a9a8b3]">Location</dt><dd className="mt-1">{lot.district}, {lot.state}</dd></div><div><dt className="text-[#a9a8b3]">Sell by</dt><dd className="mt-1">{lot.sell_by}</dd></div><div><dt className="text-[#a9a8b3]">Minimum price</dt><dd className="mt-1">{lot.minimum_price == null ? 'Not set' : `₹${lot.minimum_price.toLocaleString('en-IN')}/q`}</dd></div><div><dt className="text-[#a9a8b3]">Payment</dt><dd className="mt-1">Within {lot.max_payment_days} days</dd></div></dl><Link to={`/opportunities/${lot.id}`} className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-[#d6a84f]">View opportunities <ArrowRight className="h-4 w-4" /></Link></article>)}</div>}
  </Page>;
}

function Page({ title, copy, children }: { title: string; copy: string; children: React.ReactNode }) {
  return <div className="page-container min-h-screen"><div className="mb-8 flex flex-col gap-4 border-b border-white/10 pb-6 sm:flex-row sm:items-end sm:justify-between"><div><p className="text-xs uppercase tracking-[0.18em] text-[#8b5cf6]">KrishiX</p><h1 className="mt-2 text-4xl font-semibold">{title}</h1><p className="mt-2 max-w-xl text-sm leading-6 text-[#a9a8b3]">{copy}</p></div><Link to="/sell" className="btn-primary self-start"><PackagePlus className="h-4 w-4" /> Add produce</Link></div>{children}</div>;
}
function Loading() { return <div className="flex items-center gap-2 border border-white/10 bg-[#15182a] p-8 text-sm text-[#a9a8b3]"><Loader2 className="h-4 w-4 animate-spin" /> Loading your lots...</div>; }
function Empty() { return <div className="border border-dashed border-white/15 bg-[#15182a] p-10 text-center"><p className="text-lg font-medium">No produce yet</p><p className="mt-2 text-sm text-[#a9a8b3]">Add your first lot to start comparing selling opportunities.</p><Link to="/sell" className="btn-primary mt-5">Add produce</Link></div>; }
