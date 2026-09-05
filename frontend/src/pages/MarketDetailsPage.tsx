import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, MapPin, Package, TrendingDown, TrendingUp } from 'lucide-react';
import { dataService, inrPerQ, type Market } from '../lib/mockData';
import { Eyebrow, PriceChart, Spinner } from '../components/ui/primitives';
import { useToast } from '../context/ToastContext';

const MarketDetailsPage: React.FC = () => {
  const { id } = useParams();
  const { showToast } = useToast();
  const [market, setMarket] = useState<Market | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    dataService.getMarket(id).then((m) => {
      setMarket(m);
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

  if (!market) {
    return (
      <div className="mx-auto max-w-md py-20 text-center">
        <h1 className="text-h2 font-display">Market not found</h1>
        <Link to="/markets" className="btn btn-primary mt-6">Back to markets</Link>
      </div>
    );
  }

  const up = market.changePct >= 0;
  const prices = market.history.map((h) => h.price);
  const low = Math.min(...prices);
  const high = Math.max(...prices);

  return (
    <div className="space-y-8">
      <Link to="/markets" className="inline-flex items-center gap-1.5 text-sm" style={{ color: 'var(--text-secondary)' }}>
        <ArrowLeft size={16} /> Back to markets
      </Link>

      <div className="relative overflow-hidden rounded-2xl border" style={{ borderColor: 'var(--border)' }}>
        <img src={market.image} alt={market.name} className="h-48 w-full object-cover md:h-56" />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(180deg, rgba(8,11,20,0.2), rgba(8,11,20,0.92))' }} />
        <div className="absolute inset-x-0 bottom-0 p-6 md:p-8">
          <h1 className="text-h1 font-display text-cream">{market.name}</h1>
          <p className="mt-2 flex items-center gap-1.5 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <MapPin size={14} /> {market.district}, {market.state} · {market.distanceKm} km away
          </p>
        </div>
      </div>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="card p-5">
          <p className="text-eyebrow mb-2">Modal price · {market.priceDate}</p>
          <p className="text-h2 font-display tnum leading-none">{inrPerQ(market.lastPrice)}</p>
          <p className="mt-2 flex items-center gap-1 text-sm tnum" style={{ color: up ? 'var(--emerald)' : 'var(--burgundy)' }}>
            {up ? <TrendingUp size={14} /> : <TrendingDown size={14} />} {up ? '+' : ''}{market.changePct}% this week
          </p>
        </div>
        <div className="card p-5">
          <p className="text-eyebrow mb-2">7-day range</p>
          <p className="text-h2 font-display tnum leading-none">{inrPerQ(low)}</p>
          <p className="mt-2 text-sm tnum" style={{ color: 'var(--text-secondary)' }}>to {inrPerQ(high)}</p>
        </div>
        <div className="card p-5">
          <p className="text-eyebrow mb-2">Arrivals</p>
          <p className="text-h2 font-display tnum leading-none">{market.arrivalsQuintal.toLocaleString('en-IN')}</p>
          <p className="mt-2 flex items-center gap-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            <Package size={14} /> quintal / day
          </p>
        </div>
      </section>

      <section className="card p-6">
        <div className="mb-5 flex items-center justify-between">
          <div>
            <Eyebrow>Price trend</Eyebrow>
            <h2 className="text-h4 mt-1">Last 7 days</h2>
          </div>
        </div>
        <PriceChart data={market.history} height={260} />
      </section>

      <section className="card p-6">
        <h2 className="text-h4 mb-4">Traded here</h2>
        <div className="flex flex-wrap gap-2">
          {market.crops.map((c) => (
            <span key={c} className="badge badge-muted">{c}</span>
          ))}
        </div>
        <button
          onClick={() => showToast(`${market.name} saved`, 'success')}
          className="btn btn-outline mt-6"
        >
          Save this market
        </button>
      </section>
    </div>
  );
};

export default MarketDetailsPage;
