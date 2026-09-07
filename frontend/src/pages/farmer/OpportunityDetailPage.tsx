import React, { useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle2, Loader2, ShieldAlert } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { lotAPI, type FarmerLot, type Opportunity, type WhatIfResult } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

export default function OpportunityDetailPage() {
  const { opportunityId } = useParams();
  const toast = useToast();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [lot, setLot] = useState<FarmerLot | null>(null);
  const [loading, setLoading] = useState(true);
  const [offering, setOffering] = useState(false);
  const [extraQuantity, setExtraQuantity] = useState('');
  const [whatIf, setWhatIf] = useState<WhatIfResult | null>(null);
  const [checkingWhatIf, setCheckingWhatIf] = useState(false);

  useEffect(() => {
    if (!opportunityId) return;
    lotAPI.getOpportunity(opportunityId)
      .then((result) => { setOpportunity(result); return lotAPI.getLot(result.lot_id); })
      .then(setLot)
      .catch((error: Error) => toast.error(error.message))
      .finally(() => setLoading(false));
  }, [opportunityId, toast]);

  if (loading) return <div className="page-container min-h-screen"><div className="flex items-center gap-2 text-sm text-[#a9a8b3]"><Loader2 className="h-4 w-4 animate-spin" /> Loading opportunity...</div></div>;
  if (!opportunity) return <div className="page-container min-h-screen"><p className="text-[#a9a8b3]">This opportunity is unavailable.</p><Link to="/produce" className="btn-primary mt-5">Back to produce</Link></div>;
  const ready = opportunity.feasibility_decision === 'EXECUTABLE';
  const recoverable = opportunity.feasibility_decision === 'RECOVERABLE';
  const makeOffer = async () => {
    setOffering(true);
    try {
      await lotAPI.offerFromOpportunity(opportunity.id);
      toast.success('Offer created. Track its status in Activity.');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unable to create offer');
    } finally {
      setOffering(false);
    }
  };
  const runWhatIf = async () => {
    if (!opportunity || !lot || !extraQuantity) return;
    setCheckingWhatIf(true);
    try {
      const result = await lotAPI.whatIf(lot.id, { extra_quantity_kg: Number(extraQuantity) });
      setWhatIf(result);
      toast.success('Backend rechecked the opportunity without changing your lot.');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unable to run what-if check');
    } finally {
      setCheckingWhatIf(false);
    }
  };
  return <div className="page-container min-h-screen"><Link to={`/opportunities/${opportunity.lot_id}`} className="mb-6 inline-flex items-center gap-2 text-sm text-[#a9a8b3] hover:text-white"><ArrowLeft className="h-4 w-4" /> Back to opportunities</Link><div className="mb-8 border-b border-white/10 pb-6"><p className="text-xs uppercase tracking-[0.18em] text-[#8b5cf6]">Opportunity detail</p><h1 className="mt-2 text-4xl font-semibold">Can this sale work?</h1><p className="mt-2 text-sm text-[#a9a8b3]">{opportunity.title || opportunity.opportunity_type} · {lot?.commodity_name || 'Lot'} · {lot?.quantity_kg || (lot?.quantity || 0) * 100} kg</p></div><div className="grid gap-5 lg:grid-cols-[1.15fr_0.85fr]"><section className="border border-white/10 bg-[#15182a] p-6"><div className={`border p-5 ${ready ? 'border-emerald-400/30 bg-emerald-500/10' : recoverable ? 'border-[#d6a84f]/30 bg-[#24152f]' : 'border-rose-400/30 bg-rose-500/10'}`}><p className="text-xs uppercase tracking-[0.16em] text-[#a9a8b3]">Decision</p><p className="mt-2 text-2xl font-semibold">{ready ? 'Ready to sell' : recoverable ? 'Can work with a change' : opportunity.feasibility_decision === 'INSUFFICIENT_DATA' ? 'More data needed' : "Won't work currently"}</p><p className="mt-2 text-sm text-[#a9a8b3]">{ready ? 'This opportunity currently satisfies the requirements of your lot.' : recoverable ? 'This opportunity may become executable if the blocking requirement is addressed.' : 'This opportunity does not currently satisfy the required conditions.'}</p></div><div className="mt-6 grid gap-3 sm:grid-cols-3"><Metric label="Price" value={opportunity.offered_price == null ? 'Unavailable' : `₹${opportunity.offered_price.toLocaleString('en-IN')}/q`} /><Metric label="Estimated net realization" value={opportunity.estimated_net_realization == null ? 'Unavailable' : `₹${opportunity.estimated_net_realization.toLocaleString('en-IN')}`} /><Metric label="Source" value={opportunity.source_type || 'Unavailable'} /></div>{opportunity.explanation && <p className="mt-6 text-sm leading-6 text-[#a9a8b3]">{opportunity.explanation}</p>}{ready && <button onClick={makeOffer} disabled={offering} className="btn-primary mt-6">{offering ? 'Creating offer...' : 'Make offer'}</button>}</section><aside className="space-y-5"><section className="border border-white/10 bg-[#15182a] p-5"><h2 className="text-lg font-semibold">Why?</h2>{opportunity.blocking_constraints.length ? <div className="mt-4 space-y-3">{opportunity.blocking_constraints.map((constraint) => <div key={constraint} className="flex items-start gap-2 text-sm text-rose-200"><ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" /> {constraint}</div>)}</div> : <p className="mt-4 flex items-center gap-2 text-sm text-emerald-200"><CheckCircle2 className="h-4 w-4" /> No blocking constraints were returned.</p>}</section><section className="border border-white/10 bg-[#15182a] p-5"><h2 className="text-lg font-semibold">What-if recheck</h2><p className="mt-2 text-sm text-[#a9a8b3]">Simulate aggregation through the backend without changing this lot.</p><div className="mt-4 flex gap-2"><input type="number" min="0" value={extraQuantity} onChange={(event) => setExtraQuantity(event.target.value)} placeholder="Extra kg" className="min-w-0 flex-1 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white outline-none" /><button onClick={runWhatIf} disabled={!extraQuantity || checkingWhatIf} className="rounded-xl bg-[#8b5cf6] px-3 py-2 text-sm font-semibold text-white disabled:opacity-50">{checkingWhatIf ? 'Checking...' : 'Recheck'}</button></div>{whatIf && <div className="mt-4 border-t border-white/10 pt-4"><p className="text-xs uppercase tracking-[0.14em] text-[#a9a8b3]">Backend result</p><p className="mt-2 text-sm text-white">{whatIf.summary.executable} executable · {whatIf.summary.recoverable} recoverable · {whatIf.summary.not_viable} not viable</p><p className="mt-2 text-xs text-[#a9a8b3]">{whatIf.note}</p></div>}</section>{opportunity.minimum_viable_changes.length > 0 && <section className="border border-white/10 bg-[#15182a] p-5"><h2 className="text-lg font-semibold">What would make this work?</h2><div className="mt-4 space-y-3">{opportunity.minimum_viable_changes.map((change, index) => <p key={index} className="flex items-start gap-2 text-sm text-[#a9a8b3]"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[#d6a84f]" /> {change.description || 'Review the backend-supported recovery option.'}</p>)}</div></section>}</aside></div></div>;
}

function Metric({ label, value }: { label: string; value: string }) { return <div className="bg-white/5 p-3"><p className="text-xs text-[#a9a8b3]">{label}</p><p className="mt-1 font-semibold">{value}</p></div>; }
