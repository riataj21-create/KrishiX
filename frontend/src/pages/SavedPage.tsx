import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Bookmark, MapPin } from 'lucide-react';
import { dataService, inrPerQ, type Market, type Opportunity } from '../lib/mockData';
import { EmptyState, Eyebrow, FeasibilityBadge, Skeleton } from '../components/ui/primitives';

type Tab = 'opportunities' | 'markets';

const SavedPage: React.FC = () => {
  const [tab, setTab] = useState<Tab>('opportunities');
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([dataService.getSavedOpportunities(), dataService.getSavedMarkets()]).then(([o, m]) => {
      setOpps(o);
      setMarkets(m);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8">
      <header>
        <Eyebrow>Your shortlist</Eyebrow>
        <h1 className="text-h1 font-display mt-2">Saved</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Buyers and mandis you are keeping an eye on.
        </p>
      </header>

      <div className="flex gap-2">
        <button onClick={() => setTab('opportunities')} className={`btn btn-sm ${tab === 'opportunities' ? 'btn-primary' : 'btn-outline'}`}>
          Opportunities
        </button>
        <button onClick={() => setTab('markets')} className={`btn btn-sm ${tab === 'markets' ? 'btn-primary' : 'btn-outline'}`}>
          Markets
        </button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[0, 1].map((i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
      ) : tab === 'opportunities' ? (
        opps.length === 0 ? (
          <EmptyState icon={<Bookmark size={24} />} title="Nothing saved yet" message="Save opportunities to compare them side by side later." />
        ) : (
          <div className="space-y-3">
            {opps.map((o) => (
              <Link key={o.id} to={`/opportunities/${o.id}`} className="card card-hover flex items-center gap-4 p-4">
                <img src={o.cropImage} alt={o.cropName} className="h-16 w-16 flex-none rounded-xl object-cover" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate font-medium">{o.buyerName}</p>
                    <FeasibilityBadge status={o.feasibility} />
                  </div>
                  <p className="mt-0.5 flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <MapPin size={12} /> {o.cropName} · {o.location} · {o.distanceKm} km
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-h5 tnum">{inrPerQ(o.netRealization)}</p>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>net</p>
                </div>
                <ArrowUpRight size={16} style={{ color: 'var(--text-muted)' }} />
              </Link>
            ))}
          </div>
        )
      ) : markets.length === 0 ? (
        <EmptyState icon={<Bookmark size={24} />} title="No saved markets" message="Save mandis to track their prices over time." />
      ) : (
        <div className="space-y-3">
          {markets.map((m) => (
            <Link key={m.id} to={`/markets/${m.id}`} className="card card-hover flex items-center gap-4 p-4">
              <img src={m.image} alt={m.name} className="h-16 w-16 flex-none rounded-xl object-cover" />
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{m.name}</p>
                <p className="mt-0.5 flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                  <MapPin size={12} /> {m.district} · {m.distanceKm} km
                </p>
              </div>
              <div className="text-right">
                <p className="text-h5 tnum">{inrPerQ(m.lastPrice)}</p>
                <p className="text-xs tnum" style={{ color: m.changePct >= 0 ? 'var(--emerald)' : 'var(--burgundy)' }}>
                  {m.changePct >= 0 ? '+' : ''}{m.changePct}%
                </p>
              </div>
              <ArrowUpRight size={16} style={{ color: 'var(--text-muted)' }} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default SavedPage;
