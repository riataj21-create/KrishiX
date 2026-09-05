import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  Check,
  CircleGauge,
  Clock,
  Minus,
  RotateCcw,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import {
  CROPS,
  dataService,
  inr,
  inrPerQ,
  type AnalysisResult,
} from '../lib/mockData';
import { Eyebrow, Spinner } from '../components/ui/primitives';

type Phase = 'form' | 'loading' | 'result';

const factorIcon = (tone: 'up' | 'down' | 'neutral') =>
  tone === 'up' ? <TrendingUp size={15} /> : tone === 'down' ? <TrendingDown size={15} /> : <Minus size={15} />;
const factorColor = (tone: 'up' | 'down' | 'neutral') =>
  tone === 'up' ? 'var(--emerald)' : tone === 'down' ? 'var(--burgundy)' : 'var(--text-muted)';

const AnalyzerPage: React.FC = () => {
  const [phase, setPhase] = useState<Phase>('form');
  const [crop, setCrop] = useState('Tomato');
  const [quantity, setQuantity] = useState('60');
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const run = async (e: React.FormEvent) => {
    e.preventDefault();
    setPhase('loading');
    const res = await dataService.analyze(crop, Number(quantity) || 0);
    setResult(res);
    setPhase('result');
  };

  const reset = () => {
    setResult(null);
    setPhase('form');
  };

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <header className="text-center">
        <div className="mx-auto mb-4 inline-flex items-center gap-2 badge badge-violet">
          <Sparkles size={13} /> Analyzer
        </div>
        <h1 className="text-h1 font-display">Should you sell now, and where?</h1>
        <p className="mx-auto mt-2 max-w-md text-sm" style={{ color: 'var(--text-secondary)' }}>
          One question about your crop. One clear, cost-adjusted recommendation.
        </p>
      </header>

      {phase === 'form' && (
        <form onSubmit={run} className="card animate-in space-y-6 p-6 md:p-8">
          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="crop">Which crop?</label>
              <select id="crop" className="select" value={crop} onChange={(e) => setCrop(e.target.value)}>
                {CROPS.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="qty">How much (quintal)?</label>
              <input
                id="qty"
                type="number"
                min="1"
                required
                className="input"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
              />
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-lg w-full">
            Analyze <ArrowRight size={18} />
          </button>
        </form>
      )}

      {phase === 'loading' && (
        <div className="card flex flex-col items-center justify-center gap-4 py-20 animate-in">
          <Spinner className="h-8 w-8" />
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            Comparing prices, distance and selling costs…
          </p>
        </div>
      )}

      {phase === 'result' && result && (
        <div className="space-y-6 animate-in">
          {/* Verdict */}
          <section
            className="relative overflow-hidden rounded-2xl border p-7 md:p-8"
            style={{ borderColor: 'var(--border)', background: 'linear-gradient(135deg, var(--aubergine), var(--surface))' }}
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="badge badge-emerald">
                {result.timing === 'sell_now' ? 'Sell now' : 'Consider holding'}
              </span>
              <span className="badge badge-violet"><CircleGauge size={13} /> {result.confidence}% confidence</span>
            </div>
            <p className="mt-4 text-eyebrow">Best destination for {result.quantityQuintal} q of {result.cropName}</p>
            <h2 className="text-h1 font-display mt-1">{result.bestMarketName}</h2>
            <div className="mt-5 flex flex-wrap items-end gap-x-10 gap-y-4">
              <div>
                <p className="text-eyebrow">Net in hand</p>
                <p className="text-h1 font-display tnum" style={{ color: '#4fd7ac' }}>{inrPerQ(result.netRealization)}</p>
              </div>
              <div>
                <p className="text-eyebrow">Estimated total</p>
                <p className="text-h2 font-display tnum">{inr(result.netRealization * result.quantityQuintal)}</p>
              </div>
            </div>
          </section>

          {/* Timing note */}
          <section className="panel flex gap-3 p-5">
            <Clock size={18} className="mt-0.5 flex-none" style={{ color: 'var(--gold)' }} />
            <div>
              <h3 className="text-h5">On timing</h3>
              <p className="mt-1 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{result.timingNote}</p>
            </div>
          </section>

          {/* Factors */}
          <section className="card p-6">
            <h3 className="text-h4 mb-4">What drove this</h3>
            <div className="grid gap-3 sm:grid-cols-2">
              {result.factors.map((f) => (
                <div
                  key={f.label}
                  className="flex items-center justify-between rounded-xl p-4"
                  style={{ background: 'var(--midnight)' }}
                >
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{f.label}</span>
                  <span className="flex items-center gap-1.5 text-sm font-semibold tnum" style={{ color: factorColor(f.tone) }}>
                    {factorIcon(f.tone)} {f.value}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* Alternatives */}
          <section className="card p-6">
            <h3 className="text-h4 mb-4">Other markets, compared</h3>
            <div className="space-y-2">
              <div
                className="flex items-center justify-between rounded-xl p-4"
                style={{ background: 'var(--emerald-soft)' }}
              >
                <div className="flex items-center gap-2">
                  <Check size={16} style={{ color: '#4fd7ac' }} />
                  <div>
                    <p className="text-sm font-medium">{result.bestMarketName}</p>
                    <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Recommended</p>
                  </div>
                </div>
                <p className="text-h4 tnum" style={{ color: '#4fd7ac' }}>{inrPerQ(result.netRealization)}</p>
              </div>
              {result.alternatives.map((a) => (
                <Link
                  key={a.marketId}
                  to={`/markets/${a.marketId}`}
                  className="flex items-center justify-between rounded-xl p-4 transition-colors hover:bg-elevated"
                  style={{ background: 'var(--midnight)' }}
                >
                  <div>
                    <p className="text-sm font-medium">{a.marketName}</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{a.distanceKm} km away</p>
                  </div>
                  <p className="text-h5 tnum" style={{ color: 'var(--text-secondary)' }}>{inrPerQ(a.net)}</p>
                </Link>
              ))}
            </div>
          </section>

          <div className="flex flex-wrap gap-3">
            <Link to="/opportunities" className="btn btn-primary">
              See matching buyers <ArrowRight size={18} />
            </Link>
            <button onClick={reset} className="btn btn-outline">
              <RotateCcw size={16} /> New analysis
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyzerPage;
