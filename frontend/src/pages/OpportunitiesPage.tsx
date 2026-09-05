import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Handshake, MapPin, BadgeCheck } from 'lucide-react';
import {
  dataService,
  feasibilityMeta,
  inrPerQ,
  type Feasibility,
  type Opportunity,
} from '../lib/mockData';
import { CardSkeleton, EmptyState, Eyebrow, FeasibilityBadge } from '../components/ui/primitives';

const filters: { key: Feasibility | 'all'; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'executable', label: 'Executable' },
  { key: 'recoverable', label: 'Recoverable' },
  { key: 'not_viable', label: 'Not viable' },
  { key: 'insufficient', label: 'No data' },
];

const OpportunitiesPage: React.FC = () => {
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [active, setActive] = useState<Feasibility | 'all'>('all');

  useEffect(() => {
    dataService.getOpportunities().then((o) => {
      setOpps(o);
      setLoading(false);
    });
  }, []);

  const visible = useMemo(
    () =>
      [...opps]
        .filter((o) => active === 'all' || o.feasibility === active)
        .sort((a, b) => b.netRealization - a.netRealization),
    [opps, active],
  );

  return (
    <div className="space-y-8">
      <header>
        <Eyebrow>Buyers matched to your produce</Eyebrow>
        <h1 className="text-h1 font-display mt-2">Opportunities</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Ranked by net price in your hand — after transport, commission and labour.
        </p>
      </header>

      <div className="flex flex-wrap gap-2">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setActive(f.key)}
            className={`btn btn-sm ${active === f.key ? 'btn-primary' : 'btn-outline'}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => <CardSkeleton key={i} />)}
        </div>
      ) : visible.length === 0 ? (
        <EmptyState
          icon={<Handshake size={24} />}
          title="No opportunities here"
          message="Try a different filter, or list more produce so we can match you to more buyers."
        />
      ) : (
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {visible.map((o) => {
            const hasData = o.feasibility !== 'insufficient';
            return (
              <Link
                key={o.id}
                to={`/opportunities/${o.id}`}
                className="card card-hover overflow-hidden"
                style={{ borderTop: `2px solid ${feasibilityMeta[o.feasibility].tone}` }}
              >
                <div className="relative h-36">
                  <img src={o.cropImage} alt={o.cropName} className="h-full w-full object-cover" />
                  <div className="absolute left-3 top-3">
                    <FeasibilityBadge status={o.feasibility} />
                  </div>
                </div>
                <div className="p-5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1.5">
                      <h3 className="text-h5">{o.buyerName}</h3>
                      {o.verified && <BadgeCheck size={15} style={{ color: 'var(--emerald)' }} />}
                    </div>
                    <ArrowUpRight size={16} style={{ color: 'var(--text-muted)' }} />
                  </div>
                  <p className="mt-1 flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                    <MapPin size={12} /> {o.cropName} · {o.location} · {o.distanceKm} km
                  </p>
                  <div className="mt-4 border-t pt-4" style={{ borderColor: 'var(--border)' }}>
                    {hasData ? (
                      <div className="flex items-end justify-between">
                        <div>
                          <p className="text-eyebrow">Net in hand</p>
                          <p className="text-h3 font-display tnum">{inrPerQ(o.netRealization)}</p>
                        </div>
                        <p className="text-xs tnum" style={{ color: 'var(--text-muted)' }}>offer {inrPerQ(o.grossPrice)}</p>
                      </div>
                    ) : (
                      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                        Not enough recent price data to score this buyer.
                      </p>
                    )}
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

export default OpportunitiesPage;
