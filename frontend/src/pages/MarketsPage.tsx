import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, MapPin, TrendingDown, TrendingUp } from 'lucide-react';
import { dataService, inrPerQ, type Market } from '../lib/mockData';
import { CardSkeleton, Eyebrow } from '../components/ui/primitives';

const MarketsPage: React.FC = () => {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataService.getMarkets().then((m) => {
      setMarkets(m);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8">
      <header>
        <Eyebrow>Mandi prices near you</Eyebrow>
        <h1 className="text-h1 font-display mt-2">Markets</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Recent modal prices, arrivals and week-on-week trend for nearby mandis.
        </p>
      </header>

      {loading ? (
        <div className="grid gap-5 md:grid-cols-2">
          {[0, 1, 2, 3].map((i) => <CardSkeleton key={i} />)}
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-2">
          {markets.map((m) => {
            const up = m.changePct >= 0;
            return (
              <Link key={m.id} to={`/markets/${m.id}`} className="card card-hover overflow-hidden">
                <div className="flex gap-0">
                  <img src={m.image} alt={m.name} className="h-full w-32 flex-none object-cover" />
                  <div className="flex-1 p-5">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-h5">{m.name}</h3>
                        <p className="mt-0.5 flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                          <MapPin size={12} /> {m.district} · {m.distanceKm} km
                        </p>
                      </div>
                      <ArrowUpRight size={16} style={{ color: 'var(--text-muted)' }} />
                    </div>
                    <div className="mt-4 flex items-end justify-between">
                      <div>
                        <p className="text-eyebrow">Modal price</p>
                        <p className="text-h3 font-display tnum">{inrPerQ(m.lastPrice)}</p>
                      </div>
                      <span
                        className="flex items-center gap-1 text-sm font-medium tnum"
                        style={{ color: up ? 'var(--emerald)' : 'var(--burgundy)' }}
                      >
                        {up ? <TrendingUp size={15} /> : <TrendingDown size={15} />}
                        {up ? '+' : ''}{m.changePct}%
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MarketsPage;
