import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  ArrowLeft,
  BadgeCheck,
  CalendarClock,
  Check,
  Lightbulb,
  MapPin,
  TriangleAlert,
} from 'lucide-react';
import {
  dataService,
  feasibilityMeta,
  inr,
  inrPerQ,
  type Opportunity,
} from '../lib/mockData';
import { Eyebrow, FeasibilityBadge, Spinner } from '../components/ui/primitives';
import { useToast } from '../context/ToastContext';

const CostRow: React.FC<{ label: string; value: number; positive?: boolean }> = ({ label, value, positive }) => (
  <div className="flex items-center justify-between py-2.5 text-sm">
    <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
    <span className="tnum font-medium" style={{ color: positive ? 'var(--emerald)' : 'var(--text-primary)' }}>
      {positive ? '' : '– '}{inrPerQ(value)}
    </span>
  </div>
);

const OpportunityDetailsPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [opp, setOpp] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    dataService.getOpportunity(id).then((o) => {
      setOpp(o);
      setLoading(false);
    });
  }, [id]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center" style={{ color: 'var(--text-secondary)' }}>
        <Spinner className="h-6 w-6" />
      </div>
    );
  }

  if (!opp) {
    return (
      <div className="mx-auto max-w-md py-20 text-center">
        <h1 className="text-h2 font-display">Opportunity not found</h1>
        <Link to="/opportunities" className="btn btn-primary mt-6">Back to opportunities</Link>
      </div>
    );
  }

  const meta = feasibilityMeta[opp.feasibility];
  const hasData = opp.feasibility !== 'insufficient';
  const totalCosts = opp.costs.transport + opp.costs.commission + opp.costs.labour + opp.costs.other;
  const totalValue = opp.netRealization * opp.quantityNeededQuintal;

  const sendOffer = () => {
    showToast('Offer sent — you will be notified when the buyer responds', 'success');
    navigate(`/transaction/${opp.id}`);
  };

  return (
    <div className="space-y-8">
      <Link to="/opportunities" className="inline-flex items-center gap-1.5 text-sm" style={{ color: 'var(--text-secondary)' }}>
        <ArrowLeft size={16} /> Back to opportunities
      </Link>

      {/* Hero */}
      <div className="relative overflow-hidden rounded-2xl border" style={{ borderColor: 'var(--border)' }}>
        <img src={opp.cropImage} alt={opp.cropName} className="h-56 w-full object-cover md:h-64" />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, rgba(8,11,20,0.2), rgba(8,11,20,0.92))' }} />
        <div className="absolute inset-x-0 bottom-0 p-6 md:p-8">
          <div className="mb-3"><FeasibilityBadge status={opp.feasibility} /></div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-h1 font-display text-cream">{opp.buyerName}</h1>
            {opp.verified && <BadgeCheck size={22} style={{ color: 'var(--emerald)' }} />}
          </div>
          <p className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <span>{opp.buyerType}</span>
            <span className="flex items-center gap-1.5"><MapPin size={13} /> {opp.location} · {opp.distanceKm} km</span>
            <span className="flex items-center gap-1.5"><CalendarClock size={13} /> By {opp.deadline}</span>
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Left: reasoning */}
        <div className="space-y-6 lg:col-span-3">
          {/* Why this verdict */}
          <section className="card p-6">
            <h2 className="text-h4 mb-4">Why we graded this {meta.label.toLowerCase()}</h2>
            <ul className="space-y-3">
              {opp.reasons.map((r, i) => (
                <li key={i} className="flex gap-3 text-sm" style={{ color: 'var(--text-secondary)' }}>
                  <span
                    className="mt-0.5 flex h-5 w-5 flex-none items-center justify-center rounded-full"
                    style={{ background: meta.tone + '22', color: meta.tone }}
                  >
                    {opp.feasibility === 'not_viable' ? <TriangleAlert size={12} /> : <Check size={12} />}
                  </span>
                  {r}
                </li>
              ))}
            </ul>
          </section>

          {/* Recovery steps */}
          {opp.recovery && opp.recovery.length > 0 && (
            <section className="panel p-6" style={{ borderColor: 'rgba(214,168,79,0.35)' }}>
              <div className="mb-3 flex items-center gap-2">
                <Lightbulb size={18} style={{ color: 'var(--gold)' }} />
                <h2 className="text-h4">How to make it work</h2>
              </div>
              <ul className="space-y-2.5">
                {opp.recovery.map((r, i) => (
                  <li key={i} className="flex gap-3 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <span className="tnum font-semibold" style={{ color: 'var(--gold)' }}>{i + 1}.</span>
                    {r}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {/* Cost breakdown */}
          {hasData && (
            <section className="card p-6">
              <h2 className="text-h4 mb-2">From offer to your hand</h2>
              <p className="mb-4 text-xs" style={{ color: 'var(--text-muted)' }}>Per quintal</p>
              <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
                <CostRow label="Buyer offer" value={opp.grossPrice} positive />
                <CostRow label="Transport" value={opp.costs.transport} />
                <CostRow label="Commission" value={opp.costs.commission} />
                <CostRow label="Labour / handling" value={opp.costs.labour} />
                <CostRow label="Other charges" value={opp.costs.other} />
              </div>
              <div
                className="mt-4 flex items-center justify-between rounded-xl p-4"
                style={{ background: 'var(--emerald-soft)' }}
              >
                <div>
                  <p className="text-eyebrow" style={{ color: '#4fd7ac' }}>Net in hand</p>
                  <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>after {inrPerQ(totalCosts)} costs</p>
                </div>
                <p className="text-h2 font-display tnum" style={{ color: '#4fd7ac' }}>{inrPerQ(opp.netRealization)}</p>
              </div>
            </section>
          )}
        </div>

        {/* Right: sticky action */}
        <div className="lg:col-span-2">
          <div className="card sticky top-6 p-6">
            <Eyebrow>Deal summary</Eyebrow>
            <div className="mt-4 space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span style={{ color: 'var(--text-secondary)' }}>Crop</span>
                <span className="font-medium">{opp.cropName}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span style={{ color: 'var(--text-secondary)' }}>Quantity needed</span>
                <span className="tnum font-medium">{opp.quantityNeededQuintal} q</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span style={{ color: 'var(--text-secondary)' }}>Net per quintal</span>
                <span className="tnum font-medium">{hasData ? inrPerQ(opp.netRealization) : '—'}</span>
              </div>
              <div className="hr my-2" />
              <div className="flex items-center justify-between">
                <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Estimated total</span>
                <span className="text-h3 font-display tnum">{hasData ? inr(totalValue) : '—'}</span>
              </div>
            </div>

            <div className="mt-6 space-y-2.5">
              <button
                onClick={sendOffer}
                disabled={opp.feasibility === 'insufficient'}
                className="btn btn-primary btn-lg w-full"
              >
                Send offer
              </button>
              <button
                onClick={() => showToast('Saved to your list', 'success')}
                className="btn btn-outline w-full"
              >
                Save for later
              </button>
            </div>
            {opp.feasibility === 'not_viable' && (
              <p className="mt-3 text-center text-xs" style={{ color: 'var(--burgundy)' }}>
                We advise against this deal at current costs.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpportunityDetailsPage;
