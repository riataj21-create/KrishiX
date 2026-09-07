import React, { useEffect, useState } from 'react';
import { AlertCircle, ArrowRight, Loader2, RefreshCw, TrendingDown, Zap } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { lotAPI, type AnalyzeResponse, type FarmerLot, type Opportunity } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

const DECISION_CONFIG: Record<string, { label: string; border: string; text: string; dot: string }> = {
  EXECUTABLE:        { label: 'Ready to sell',         border: 'border-emerald-400/30', text: 'text-emerald-300', dot: 'bg-emerald-400' },
  RECOVERABLE:       { label: 'Can work with changes', border: 'border-amber-400/30',   text: 'text-amber-300',   dot: 'bg-amber-400' },
  NOT_VIABLE:        { label: "Won't work currently",  border: 'border-rose-400/30',    text: 'text-rose-300',    dot: 'bg-rose-400' },
  INSUFFICIENT_DATA: { label: 'More data needed',      border: 'border-slate-400/20',   text: 'text-slate-400',   dot: 'bg-slate-400' },
};

export default function OpportunitiesPage() {
  const { lotId } = useParams();
  const toast = useToast();
  const [lot, setLot] = useState<FarmerLot | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  const load = (analyze = false) => {
    if (!lotId) return;
    setLoading(true);
    const call = analyze
      ? lotAPI.analyzeOpportunities(lotId)
      : lotAPI.getOpportunities(lotId);
    Promise.all([lotAPI.getLot(lotId), call])
      .then(([lotData, res]) => { setLot(lotData); setResult(res); })
      .catch((err: Error) => toast.error(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [lotId]);

  const runAnalysis = async () => {
    if (!lotId) return;
    setAnalyzing(true);
    try {
      const [lotData, res] = await Promise.all([
        lotAPI.getLot(lotId),
        lotAPI.analyzeOpportunities(lotId),
      ]);
      setLot(lotData);
      setResult(res);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  if (!lotId) return (
    <div className="page-container min-h-screen">
      <h1 className="text-4xl font-semibold">Opportunities</h1>
      <p className="mt-3 text-[#a9a8b3]">Choose a lot from My produce to see where it can actually be sold.</p>
      <Link to="/produce" className="btn-primary mt-6">View my produce</Link>
    </div>
  );

  const items = result?.items ?? [];
  const gap = result?.opportunity_gap;
  const summary = result?.summary;

  return (
    <div className="page-container min-h-screen">
      {/* Header */}
      <div className="mb-8 border-b border-white/10 pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-[#8b5cf6]">Decision engine</p>
        <h1 className="mt-2 text-4xl font-semibold">Opportunities</h1>
        <p className="mt-2 text-sm text-[#a9a8b3]">Ranked by what you can actually sell — not by advertised price.</p>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 border border-white/10 bg-[#15182a] p-8 text-sm text-[#a9a8b3]">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading opportunities...
        </div>
      ) : (
        <>
          {/* Lot summary + run analysis */}
          {lot && (
            <div className="mb-5 flex flex-wrap items-center justify-between gap-4 border border-white/10 bg-[#15182a] p-5">
              <div>
                <p className="text-xs uppercase tracking-[0.15em] text-[#a9a8b3]">Current lot</p>
                <p className="mt-2 text-xl font-semibold">
                  {lot.commodity_name ?? 'Lot'} · {lot.quantity_kg ?? (lot.quantity ?? 0) * 100} kg · {lot.quality_grade ?? 'Quality not specified'}
                </p>
                <p className="mt-1 text-sm text-[#a9a8b3]">{lot.district}, {lot.state} · Sell by {lot.sell_by}</p>
              </div>
              <button
                onClick={runAnalysis}
                disabled={analyzing}
                className="btn-primary flex items-center gap-2"
              >
                {analyzing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                {analyzing ? 'Analysing...' : 'Run analysis'}
              </button>
            </div>
          )}

          {/* Opportunity gap banner */}
          {gap && (
            <div className="mb-5 flex items-start gap-4 border border-[#d6a84f]/30 bg-[#1e1608] p-4">
              <TrendingDown className="mt-0.5 h-5 w-5 shrink-0 text-[#d6a84f]" />
              <div>
                <p className="text-sm font-semibold text-[#d6a84f]">Opportunity gap: ₹{gap.gap_per_kg}/kg</p>
                <p className="mt-1 text-xs text-[#a9a8b3]">
                  Highest quoted: ₹{gap.highest_quoted_per_kg}/kg — Best executable: ₹{gap.best_executable_per_kg}/kg.
                </p>
                <p className="mt-1 text-xs text-[#a9a8b3]">{gap.label}</p>
              </div>
            </div>
          )}

          {/* Summary counts */}
          {summary && summary.total > 0 && (
            <div className="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <SummaryBadge count={summary.executable} label="Executable" color="text-emerald-300" />
              <SummaryBadge count={summary.recoverable} label="Recoverable" color="text-amber-300" />
              <SummaryBadge count={summary.not_viable} label="Not viable" color="text-rose-300" />
              <SummaryBadge count={summary.insufficient_data} label="Needs data" color="text-slate-400" />
            </div>
          )}

          {/* Recommendation */}
          {result?.recommendation && (
            <div className="mb-5 border border-[#d6a84f]/20 bg-[#24152f] p-4 text-sm text-[#f5f1e8]">
              {result.recommendation}
            </div>
          )}

          {/* Opportunity cards */}
          {items.length === 0 ? (
            <div className="border border-dashed border-white/15 bg-[#15182a] p-10 text-center">
              <AlertCircle className="mx-auto h-7 w-7 text-[#a9a8b3]" />
              <p className="mt-3 text-lg font-medium">No opportunities found</p>
              <p className="mt-2 text-sm text-[#a9a8b3]">Run the analysis to discover buyers and markets for this lot.</p>
              <button onClick={runAnalysis} disabled={analyzing} className="btn-primary mt-5">
                {analyzing ? 'Running...' : 'Run analysis'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {items.map((item, i) => (
                <OpportunityCard key={item.id} item={item} rank={i + 1} />
              ))}
            </div>
          )}

          {/* Data caveat */}
          {result?.data_caveat && (
            <p className="mt-6 text-xs text-[#a9a8b3]">{result.data_caveat}</p>
          )}
        </>
      )}
    </div>
  );
}

function SummaryBadge({ count, label, color }: { count: number; label: string; color: string }) {
  return (
    <div className="border border-white/10 bg-[#15182a] p-3 text-center">
      <p className={`text-2xl font-bold ${color}`}>{count}</p>
      <p className="mt-1 text-xs text-[#a9a8b3]">{label}</p>
    </div>
  );
}

function OpportunityCard({ item, rank }: { item: Opportunity; rank: number }) {
  const cfg = DECISION_CONFIG[item.feasibility_decision] ?? DECISION_CONFIG.INSUFFICIENT_DATA;
  const isTop = rank === 1 && item.feasibility_decision === 'EXECUTABLE';

  return (
    <article className={`border p-5 ${isTop ? 'border-[#d6a84f]/40 bg-[#15182a]' : 'border-white/10 bg-[#0d1020]'}`}>
      {/* Title row */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          {isTop && (
            <p className="mb-1 flex items-center gap-1 text-xs uppercase tracking-[0.15em] text-[#d6a84f]">
              <Zap className="h-3 w-3" /> Best executable opportunity
            </p>
          )}
          <h2 className="text-xl font-semibold">{item.title ?? item.opportunity_type}</h2>
          <p className="mt-1 text-xs text-[#a9a8b3]">
            Rank #{rank} · {item.price_kind === 'buyer_offer' ? 'Buyer offer' : 'Market price'} · {item.source_type}
          </p>
        </div>
        <span className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs ${cfg.border} ${cfg.text}`}>
          <span className={`h-1.5 w-1.5 rounded-full ${cfg.dot}`} />
          {cfg.label}
        </span>
      </div>

      {/* Metrics */}
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <Metric label="Offered price" value={item.offered_price == null ? '—' : `₹${item.offered_price.toLocaleString('en-IN')}/q`} />
        <Metric
          label="Est. net realization"
          value={item.estimated_net_realization == null ? '—' : `₹${item.estimated_net_realization.toLocaleString('en-IN')}`}
          highlight={isTop}
        />
        <Metric label="Payment" value={item.payment_days == null ? '—' : item.payment_days === 0 ? 'Immediate' : `${item.payment_days} days`} />
      </div>

      {/* Blocking constraints inline summary */}
      {item.blocking_constraints.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {item.blocking_constraints.map(c => (
            <span key={c} className="rounded border border-rose-400/20 bg-rose-500/10 px-2 py-0.5 text-xs text-rose-300">{c}</span>
          ))}
        </div>
      )}

      {/* First gap explanation */}
      {item.opportunity_gaps?.length > 0 && (
        <p className="mt-3 text-xs text-[#a9a8b3]">{item.opportunity_gaps[0].explanation}</p>
      )}

      <Link
        to={`/opportunities/detail/${item.id}`}
        className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-[#d6a84f] hover:text-[#e8c06a]"
      >
        {item.feasibility_decision === 'RECOVERABLE' ? 'See how to fix this' : 'View details'}
        <ArrowRight className="h-4 w-4" />
      </Link>
    </article>
  );
}

function Metric({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div className={`p-3 ${highlight ? 'bg-[#d6a84f]/10 border border-[#d6a84f]/20' : 'bg-white/5'}`}>
      <p className="text-xs text-[#a9a8b3]">{label}</p>
      <p className={`mt-1 font-semibold ${highlight ? 'text-[#d6a84f]' : ''}`}>{value}</p>
    </div>
  );
}
