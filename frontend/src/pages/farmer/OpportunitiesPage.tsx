import React, { useEffect, useState } from 'react';
import { ArrowRight, Loader2 } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { lotAPI, type FarmerLot, type Opportunity } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

export default function OpportunitiesPage() {
  const { lotId } = useParams();
  const toast = useToast();
  const [lot, setLot] = useState<FarmerLot | null>(null);
  const [items, setItems] = useState<Opportunity[]>([]);
  const [recommendation, setRecommendation] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!lotId) { setLoading(false); return; }
    Promise.all([lotAPI.getLot(lotId), lotAPI.getOpportunities(lotId)]).then(([lotResult, result]) => { setLot(lotResult); setItems(result.items); setRecommendation(result.recommendation || ''); }).catch((error: Error) => toast.error(error.message || 'Unable to load opportunities')).finally(() => setLoading(false));
  }, [lotId, toast]);

  if (!lotId) return <div className="page-container min-h-screen"><h1 className="text-4xl font-semibold">Opportunities</h1><p className="mt-3 text-[#a9a8b3]">Choose a lot from My produce to see where it can actually be sold.</p><Link to="/produce" className="btn-primary mt-6">View my produce</Link></div>;
  return <div className="page-container min-h-screen"><div className="mb-8 border-b border-white/10 pb-6"><p className="eyebrow">Decision engine</p><h1 className="editorial-title mt-2">Where should you sell?</h1><p className="mt-2 text-sm text-[#a9a8b3]">A ranked view of the places where this harvest can realistically earn more.</p></div>{loading ? <div className="glass-panel flex items-center gap-2 p-8 text-sm text-[#a9a8b3]"><Loader2 className="h-4 w-4 animate-spin" /> Loading opportunities...</div> : <><div className="glass-panel mb-6 p-5"><p className="eyebrow">Current harvest</p><p className="mt-2 font-serif text-2xl font-semibold">{lot?.commodity_name || 'Lot'} · {lot?.quantity_kg || (lot?.quantity || 0) * 100} kg</p><p className="mt-1 text-sm text-[#a9a8b3]">{lot?.district}, {lot?.state} · Sell by {lot?.sell_by}</p></div>{recommendation && <div className="mb-6 rounded-xl border border-[#d6a84f]/30 bg-[#24152f]/80 p-4 text-sm text-[#f5f1e8]">{recommendation}</div>}{items.length === 0 ? <div className="glass-panel p-10 text-center text-sm text-[#a9a8b3]">No executable opportunities were found for this lot.</div> : <div className="space-y-4">{items.slice(0, 3).map((item, index) => <OpportunityCard key={item.id} item={item} primary={index === 0} />)}</div>}</>}</div>;
}

function OpportunityCard({ item, primary }: { item: Opportunity; primary: boolean }) {
  const label = item.feasibility_decision === 'EXECUTABLE' ? 'Ready to sell' : item.feasibility_decision === 'RECOVERABLE' ? 'Can work with a change' : item.feasibility_decision === 'NOT_VIABLE' ? "Won't work currently" : 'More data needed';
  return <article className={`glass-panel p-5 ${primary ? 'border-[#d6a84f]/50 bg-[#24152f]/80' : ''}`}><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="eyebrow">{primary ? 'Best current opportunity' : 'Alternative'}</p><h2 className="mt-2 font-serif text-2xl font-semibold">{item.title || item.opportunity_type}</h2></div><span className={`rounded-full border px-2.5 py-1 text-xs ${item.feasibility_decision === 'EXECUTABLE' ? 'border-emerald-400/30 text-emerald-300' : item.feasibility_decision === 'RECOVERABLE' ? 'border-[#d6a84f]/40 text-[#d6a84f]' : 'border-rose-400/30 text-rose-300'}`}>{label}</span></div><div className="mt-5 grid gap-3 sm:grid-cols-3"><Metric label="Price" value={item.offered_price == null ? 'Unavailable' : `₹${item.offered_price.toLocaleString('en-IN')}/q`} /><Metric label="Estimated net realization" value={item.estimated_net_realization == null ? 'Unavailable' : `₹${item.estimated_net_realization.toLocaleString('en-IN')}`} /><Metric label="Source" value={item.source_type || 'Unavailable'} /></div>{item.explanation && <p className="mt-4 text-sm leading-6 text-[#a9a8b3]">{item.explanation}</p>}<Link to={`/opportunities/detail/${item.id}`} className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-[#d6a84f]">View opportunity <ArrowRight className="h-4 w-4" /></Link></article>;
}
function Metric({ label, value }: { label: string; value: string }) { return <div className="bg-white/5 p-3"><p className="text-xs text-[#a9a8b3]">{label}</p><p className="mt-1 font-semibold">{value}</p></div>; }
