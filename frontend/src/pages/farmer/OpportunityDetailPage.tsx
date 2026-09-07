import React, { useEffect, useState } from 'react';
import {
  AlertTriangle, ArrowLeft, CheckCircle2, ChevronRight,
  Loader2, RefreshCw, ShieldAlert, TrendingDown, TrendingUp, Zap,
} from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { lotAPI, type FarmerLot, type Opportunity, type MinimumViableChange, type OpportunityGap } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

// ── Decision badge colours ────────────────────────────────────────────────────
const DECISION_STYLE: Record<string, { border: string; bg: string; text: string; label: string }> = {
  EXECUTABLE:        { border: 'border-emerald-400/40', bg: 'bg-emerald-500/10', text: 'text-emerald-300', label: 'Ready to sell' },
  RECOVERABLE:       { border: 'border-amber-400/40',  bg: 'bg-amber-500/10',   text: 'text-amber-300',  label: 'Can work with changes' },
  NOT_VIABLE:        { border: 'border-rose-400/40',   bg: 'bg-rose-500/10',    text: 'text-rose-300',   label: "Won't work currently" },
  INSUFFICIENT_DATA: { border: 'border-slate-400/30',  bg: 'bg-slate-500/10',   text: 'text-slate-300',  label: 'More data needed' },
};

const CONSTRAINT_LABEL: Record<string, string> = {
  QUANTITY: 'Quantity', QUALITY: 'Quality / Grade', PAYMENT: 'Payment terms',
  PRICE: 'Price floor', TRANSPORT: 'Transport cost', TIMING: 'Timing',
  DEADLINE: 'Deadline', MISSING_DATA: 'Missing data',
};

const RECOVERY_LABELS: Record<string, string> = {
  AGGREGATION: 'Aggregate more lots',
  NEGOTIATE_PAYMENT: 'Negotiate payment terms',
  NEGOTIATE_PRICE: 'Negotiate price',
  TRANSPORT_OPTIMIZATION: 'Optimise transport / buyer pickup',
};

export default function OpportunityDetailPage() {
  const { opportunityId } = useParams();
  const toast = useToast();
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [lot, setLot] = useState<FarmerLot | null>(null);
  const [loading, setLoading] = useState(true);
  const [offering, setOffering] = useState(false);
  const [recovering, setRecovering] = useState<string | null>(null);

  useEffect(() => {
    if (!opportunityId) return;
    lotAPI.getOpportunity(opportunityId)
      .then((result) => { setOpportunity(result); return lotAPI.getLot(result.lot_id); })
      .then(setLot)
      .catch((err: Error) => toast.error(err.message))
      .finally(() => setLoading(false));
  }, [opportunityId, toast]);

  const applyRecovery = async (changeType: string) => {
    if (!opportunity) return;
    setRecovering(changeType);
    try {
      const updated = await lotAPI.applyRecovery(opportunity.id, [changeType]);
      setOpportunity(updated);
      toast.success('Recovery applied — feasibility recalculated.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Recovery failed');
    } finally {
      setRecovering(null);
    }
  };

  const makeOffer = async () => {
    if (!opportunity) return;
    setOffering(true);
    try {
      await lotAPI.offerFromOpportunity(opportunity.id);
      toast.success('Offer created. Track progress in Activity.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Unable to create offer');
    } finally {
      setOffering(false);
    }
  };

  if (loading) return (
    <div className="page-container min-h-screen flex items-center gap-2 text-sm text-[#a9a8b3]">
      <Loader2 className="h-4 w-4 animate-spin" /> Loading opportunity...
    </div>
  );
  if (!opportunity) return (
    <div className="page-container min-h-screen">
      <p className="text-[#a9a8b3]">Opportunity not found.</p>
      <Link to="/produce" className="btn-primary mt-5">Back to produce</Link>
    </div>
  );

  const style = DECISION_STYLE[opportunity.feasibility_decision] ?? DECISION_STYLE.INSUFFICIENT_DATA;
  const isExecutable = opportunity.feasibility_decision === 'EXECUTABLE';
  const isRecoverable = opportunity.feasibility_decision === 'RECOVERABLE';

  // Feasible recovery changes only
  const feasibleChanges = (opportunity.minimum_viable_changes ?? []).filter(m => m.feasible);

  return (
    <div className="page-container min-h-screen">
      {/* Back */}
      <Link
        to={`/opportunities/${opportunity.lot_id}`}
        className="mb-6 inline-flex items-center gap-2 text-sm text-[#a9a8b3] hover:text-white"
      >
        <ArrowLeft className="h-4 w-4" /> Back to opportunities
      </Link>

      {/* Header */}
      <div className="mb-8 border-b border-white/10 pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-[#8b5cf6]">Opportunity detail</p>
        <h1 className="mt-2 text-4xl font-semibold">Can this sale work?</h1>
        <p className="mt-2 text-sm text-[#a9a8b3]">
          {opportunity.title ?? opportunity.opportunity_type}
          {lot && ` · ${lot.commodity_name ?? 'Lot'} · ${lot.quantity_kg ?? (lot.quantity ?? 0) * 100} kg`}
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">

        {/* ── Left column ── */}
        <div className="space-y-5">

          {/* Decision banner */}
          <div className={`border p-5 ${style.border} ${style.bg}`}>
            <p className="text-xs uppercase tracking-[0.15em] text-[#a9a8b3]">Decision</p>
            <p className={`mt-2 text-2xl font-semibold ${style.text}`}>{style.label}</p>
            <p className="mt-2 text-sm text-[#a9a8b3]">{opportunity.explanation}</p>
          </div>

          {/* Key metrics */}
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <Metric label="Offered price" value={opportunity.offered_price == null ? '—' : `₹${opportunity.offered_price.toLocaleString('en-IN')}/q`} sub="₹/quintal" />
            <Metric
              label="Est. net realization"
              value={opportunity.estimated_net_realization == null ? '—' : `₹${opportunity.estimated_net_realization.toLocaleString('en-IN')}`}
              sub="after labelled costs"
              highlight
            />
            <Metric label="Data source" value={opportunity.source_type ?? '—'} sub={opportunity.data_quality ?? ''} />
          </div>

          {/* Economics breakdown */}
          {opportunity.economics && (
            <section className="border border-white/10 bg-[#15182a] p-5">
              <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-[#a9a8b3]">How the net is calculated</h2>
              <div className="mt-4 space-y-2 text-sm">
                <EconRow label="Gross (offered price × lot qty)" value={`₹${opportunity.economics.sale_value.toLocaleString('en-IN')}`} />
                <EconRow label={`Transport (${opportunity.economics.transport_source})`} value={`− ₹${opportunity.economics.transport.toLocaleString('en-IN')}`} muted />
                <EconRow label="Market charges" value={`− ₹${opportunity.economics.market_charges.toLocaleString('en-IN')}`} muted />
                <EconRow label="Loading / handling" value={`− ₹${opportunity.economics.loading_handling.toLocaleString('en-IN')}`} muted />
                <div className="border-t border-white/10 pt-2">
                  <EconRow label="Estimated net realization" value={`₹${opportunity.economics.estimated_net.toLocaleString('en-IN')}`} bold />
                </div>
              </div>
              <p className="mt-3 text-xs text-[#a9a8b3]">
                Estimated realization — not a guaranteed receipt. Transport is a {opportunity.economics.transport_source} estimate.
              </p>
            </section>
          )}

          {/* Offer button */}
          {isExecutable && (
            <button onClick={makeOffer} disabled={offering} className="btn-primary w-full justify-center">
              {offering ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating offer...</> : <><Zap className="h-4 w-4" /> Make offer</>}
            </button>
          )}
        </div>

        {/* ── Right column ── */}
        <div className="space-y-5">

          {/* Blocking constraints */}
          <section className="border border-white/10 bg-[#15182a] p-5">
            <h2 className="text-lg font-semibold">Why {isExecutable ? 'it works' : "it doesn't work"}</h2>
            {opportunity.blocking_constraints.length === 0 ? (
              <p className="mt-4 flex items-center gap-2 text-sm text-emerald-300">
                <CheckCircle2 className="h-4 w-4" /> All constraints satisfied.
              </p>
            ) : (
              <div className="mt-4 space-y-4">
                {(opportunity.opportunity_gaps ?? []).map((gap, i) => (
                  <GapCard key={i} gap={gap} />
                ))}
              </div>
            )}
          </section>

          {/* Recovery options */}
          {(isRecoverable || opportunity.blocking_constraints.length > 0) && feasibleChanges.length > 0 && (
            <section className="border border-amber-400/20 bg-[#1e1608] p-5">
              <h2 className="text-lg font-semibold text-amber-300">What would make this work?</h2>
              <p className="mt-1 text-xs text-[#a9a8b3]">Smallest change to restore feasibility. Applies a simulation — your lot is not modified.</p>
              <div className="mt-4 space-y-3">
                {feasibleChanges.map((mvc, i) => (
                  <RecoveryAction
                    key={i}
                    mvc={mvc}
                    loading={recovering === mvc.change_type}
                    onApply={() => applyRecovery(mvc.change_type)}
                  />
                ))}
              </div>
            </section>
          )}

          {/* Aggregation result */}
          {opportunity.aggregation && (
            <section className="border border-[#8b5cf6]/20 bg-[#120f1e] p-5">
              <h2 className="text-lg font-semibold text-[#c4b5fd]">Aggregation</h2>
              <p className="mt-2 text-sm text-[#a9a8b3]">{opportunity.aggregation.reason}</p>
              {opportunity.aggregation.members.length > 0 && (
                <div className="mt-4 space-y-2">
                  {opportunity.aggregation.members.map((m, i) => (
                    <div key={i} className="flex items-center justify-between border border-white/10 bg-[#15182a] px-3 py-2 text-xs">
                      <span className="text-[#a9a8b3]">{m.district}</span>
                      <span className="font-medium">{m.quantity_kg} kg</span>
                      <span className="rounded-full border border-[#8b5cf6]/30 px-2 py-0.5 text-[#c4b5fd]">{m.participant_type}</span>
                    </div>
                  ))}
                  <p className="mt-2 text-xs text-[#a9a8b3]">{opportunity.aggregation.members[0]?.label}</p>
                </div>
              )}
            </section>
          )}

          {/* After-recovery: make offer */}
          {isExecutable && opportunity.applied_recovery && (
            <div className="border border-emerald-400/30 bg-emerald-500/10 p-4 text-sm text-emerald-200">
              <CheckCircle2 className="mb-2 h-4 w-4" />
              Recovery applied. This opportunity is now executable.
              <button onClick={makeOffer} disabled={offering} className="btn-primary mt-3 w-full justify-center text-sm">
                {offering ? 'Creating offer...' : 'Make offer'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Metric({ label, value, sub, highlight }: { label: string; value: string; sub?: string; highlight?: boolean }) {
  return (
    <div className={`border p-3 ${highlight ? 'border-[#d6a84f]/30 bg-[#24152f]' : 'border-white/10 bg-white/5'}`}>
      <p className="text-xs text-[#a9a8b3]">{label}</p>
      <p className={`mt-1 font-semibold ${highlight ? 'text-[#d6a84f]' : ''}`}>{value}</p>
      {sub && <p className="mt-0.5 text-xs text-[#a9a8b3]">{sub}</p>}
    </div>
  );
}

function EconRow({ label, value, muted, bold }: { label: string; value: string; muted?: boolean; bold?: boolean }) {
  return (
    <div className="flex items-center justify-between">
      <span className={`text-sm ${muted ? 'text-[#a9a8b3]' : ''}`}>{label}</span>
      <span className={`text-sm ${bold ? 'font-semibold text-[#d6a84f]' : muted ? 'text-[#a9a8b3]' : 'font-medium'}`}>{value}</span>
    </div>
  );
}

function GapCard({ gap }: { gap: OpportunityGap }) {
  return (
    <div className="border border-rose-400/20 bg-rose-500/5 p-4">
      <div className="flex items-center gap-2">
        <ShieldAlert className="h-4 w-4 shrink-0 text-rose-300" />
        <p className="text-sm font-medium text-rose-200">
          {CONSTRAINT_LABEL[gap.constraint_type] ?? gap.constraint_type}
        </p>
        <span className="ml-auto rounded-full border border-rose-400/20 px-2 py-0.5 text-xs text-rose-300">HARD</span>
      </div>
      <p className="mt-2 text-sm text-[#a9a8b3]">{gap.explanation}</p>
      {gap.gap != null && gap.gap_unit && (
        <div className="mt-3 flex items-center gap-6 text-xs">
          <span className="text-[#a9a8b3]">Required: <strong className="text-white">{String(gap.required)}</strong></span>
          <ChevronRight className="h-3 w-3 text-[#a9a8b3]" />
          <span className="text-[#a9a8b3]">Available: <strong className="text-white">{String(gap.available)}</strong></span>
          <span className="ml-auto rounded bg-rose-500/20 px-2 py-0.5 text-rose-200">
            Gap: {String(gap.gap)} {gap.gap_unit}
          </span>
        </div>
      )}
    </div>
  );
}

function RecoveryAction({ mvc, loading, onApply }: { mvc: MinimumViableChange; loading: boolean; onApply: () => void }) {
  return (
    <div className="border border-amber-400/20 bg-[#15182a] p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-amber-200">
            {RECOVERY_LABELS[mvc.change_type] ?? mvc.change_type}
          </p>
          <p className="mt-1 text-xs text-[#a9a8b3]">{mvc.description}</p>
          <p className="mt-1 text-xs text-[#a9a8b3]">{mvc.reason}</p>
        </div>
        <button
          onClick={onApply}
          disabled={loading}
          className="shrink-0 rounded border border-amber-400/30 bg-amber-500/10 px-3 py-1.5 text-xs text-amber-200 hover:bg-amber-500/20 disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : 'Apply'}
        </button>
      </div>
      {mvc.resulting_feasibility && (
        <p className="mt-2 text-xs text-[#a9a8b3]">
          Result if applied: <span className="font-medium text-amber-300">{mvc.resulting_feasibility}</span>
        </p>
      )}
    </div>
  );
}
