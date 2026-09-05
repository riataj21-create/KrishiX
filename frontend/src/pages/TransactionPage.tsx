import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { CheckCircle2, Clock, Home, Phone } from 'lucide-react';
import { dataService, inr, inrPerQ, type Opportunity } from '../lib/mockData';
import { Eyebrow, Spinner } from '../components/ui/primitives';

const steps = [
  { label: 'Offer sent', done: true },
  { label: 'Buyer review', done: false, current: true },
  { label: 'Agreement', done: false },
  { label: 'Pickup & payment', done: false },
];

const TransactionPage: React.FC = () => {
  const { id } = useParams();
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
        <h1 className="text-h2 font-display">Transaction not found</h1>
        <Link to="/home" className="btn btn-primary mt-6">Back home</Link>
      </div>
    );
  }

  const total = opp.netRealization * opp.quantityNeededQuintal;

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      {/* Confirmation */}
      <div className="card p-8 text-center animate-in">
        <div
          className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full"
          style={{ background: 'var(--emerald-soft)', color: '#4fd7ac' }}
        >
          <CheckCircle2 size={32} />
        </div>
        <Eyebrow>Offer sent</Eyebrow>
        <h1 className="text-h1 font-display mt-2">You are in the queue</h1>
        <p className="mx-auto mt-2 max-w-sm text-sm" style={{ color: 'var(--text-secondary)' }}>
          {opp.buyerName} has received your offer for {opp.quantityNeededQuintal} q of {opp.cropName}.
          You will be notified as soon as they respond.
        </p>
      </div>

      {/* Progress */}
      <div className="card p-6">
        <h2 className="text-h4 mb-5">Deal progress</h2>
        <div className="space-y-1">
          {steps.map((s, i) => (
            <div key={s.label} className="flex items-center gap-4">
              <div className="flex flex-col items-center">
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold"
                  style={{
                    background: s.done ? 'var(--emerald)' : s.current ? 'var(--gold)' : 'var(--raised)',
                    color: s.done || s.current ? '#0b0e1a' : 'var(--text-muted)',
                  }}
                >
                  {s.done ? <CheckCircle2 size={16} /> : s.current ? <Clock size={15} /> : i + 1}
                </div>
                {i < steps.length - 1 && <div className="my-1 h-6 w-px" style={{ background: 'var(--border-strong)' }} />}
              </div>
              <span
                className="text-sm"
                style={{ color: s.done || s.current ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: s.current ? 600 : 400 }}
              >
                {s.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="card p-6">
        <h2 className="text-h4 mb-4">Offer summary</h2>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between"><span style={{ color: 'var(--text-secondary)' }}>Buyer</span><span className="font-medium">{opp.buyerName}</span></div>
          <div className="flex justify-between"><span style={{ color: 'var(--text-secondary)' }}>Crop</span><span className="font-medium">{opp.cropName}</span></div>
          <div className="flex justify-between"><span style={{ color: 'var(--text-secondary)' }}>Quantity</span><span className="tnum font-medium">{opp.quantityNeededQuintal} q</span></div>
          <div className="flex justify-between"><span style={{ color: 'var(--text-secondary)' }}>Net per quintal</span><span className="tnum font-medium">{inrPerQ(opp.netRealization)}</span></div>
          <div className="hr my-1" />
          <div className="flex items-center justify-between">
            <span style={{ color: 'var(--text-secondary)' }}>Estimated total</span>
            <span className="text-h3 font-display tnum">{inr(total)}</span>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <Link to="/home" className="btn btn-primary"><Home size={16} /> Back to home</Link>
        <a href="tel:" className="btn btn-outline"><Phone size={16} /> Contact buyer</a>
      </div>
    </div>
  );
};

export default TransactionPage;
