import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ArrowUpRight, Sparkles, Sprout, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  dataService,
  inrPerQ,
  type Market,
  type Opportunity,
  type Produce,
} from '../lib/mockData';
import { CardSkeleton, Eyebrow, FeasibilityBadge, Stat } from '../components/ui/primitives';

const HomePage: React.FC = () => {
  const { user } = useAuth();
  const [produce, setProduce] = useState<Produce[]>([]);
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dataService.getProduce(),
      dataService.getOpportunities(),
      dataService.getMarkets(),
    ]).then(([p, o, m]) => {
      setProduce(p);
      setOpps(o);
      setMarkets(m);
      setLoading(false);
    });
  }, []);

  const topOpps = opps.filter((o) => o.feasibility !== 'insufficient').slice(0, 3);
  const firstName = (user?.name || 'Farmer').split(' ')[0];

  return (
    <div className="space-y-10">
      {/* Greeting */}
      <header className="animate-in">
        <Eyebrow>2 September 2026</Eyebrow>
        <h1 className="text-h1 font-display mt-2">Good morning, {firstName}.</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Here is where your crop earns the most today.
        </p>
      </header>

      {/* Stat row */}
      <section className="grid gap-4 sm:grid-cols-3">
        <Stat label="Best net today" value={inrPerQ(2412)} sub="Nashik APMC · Tomato" tone="up" />
        <Stat label="Live opportunities" value={String(opps.length)} sub="2 executable now" />
        <Stat label="Produce listed" value={String(produce.length)} sub="78 quintal total" />
      </section>

      {/* Primary action banner */}
      <section
        className="relative overflow-hidden rounded-2xl border p-7 md:p-9"
        style={{ borderColor: 'var(--border)', background: 'linear-gradient(135deg, var(--aubergine), var(--surface))' }}
      >
        <div className="relative z-10 flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div className="max-w-lg">
            <div className="mb-3 inline-flex items-center gap-2 badge badge-violet">
              <Sparkles size={13} /> Analyzer
            </div>
            <h2 className="text-h3 font-display">Should you sell now, and where?</h2>
            <p className="mt-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              Answer one question about your crop and get a ranked, cost-adjusted recommendation.
            </p>
          </div>
          <Link to="/analyzer" className="btn btn-primary btn-lg self-start">
            Run analysis <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* Best opportunities */}
      <section>
        <div className="mb-4 flex items-end justify-between">
          <div>
            <Eyebrow>Ranked by net price</Eyebrow>
            <h2 className="text-h2 font-display mt-1">Best opportunities</h2>
          </div>
          <Link to="/opportunities" className="link-accent inline-flex items-center gap-1 text-sm font-medium">
            View all <ArrowRight size={15} />
          </Link>
        </div>

        {loading ? (
          <div className="grid gap-5 md:grid-cols-3">
            {[0, 1, 2].map((i) => <CardSkeleton key={i} />)}
          </div>
        ) : (
          <div className="grid gap-5 md:grid-cols-3">
            {topOpps.map((o) => (
              <Link key={o.id} to={`/opportunities/${o.id}`} className="card card-hover overflow-hidden">
                <div className="relative h-36">
                  <img src={o.cropImage} alt={o.cropName} className="h-full w-full object-cover" />
                  <div className="absolute left-3 top-3">
                    <FeasibilityBadge status={o.feasibility} />
                  </div>
                </div>
                <div className="p-5">
                  <div className="flex items-center justify-between">
                    <h3 className="text-h5">{o.buyerName}</h3>
                    <ArrowUpRight size={16} style={{ color: 'var(--text-muted)' }} />
                  </div>
                  <p className="mt-0.5 text-xs" style={{ color: 'var(--text-muted)' }}>
                    {o.cropName} · {o.location} · {o.distanceKm} km
                  </p>
                  <div className="mt-4 flex items-end justify-between">
                    <div>
                      <p className="text-eyebrow">Net in hand</p>
                      <p className="text-h3 font-display tnum">{inrPerQ(o.netRealization)}</p>
                    </div>
                    <p className="text-xs tnum" style={{ color: 'var(--text-muted)' }}>
                      offer {inrPerQ(o.grossPrice)}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Movers + your produce */}
      <section className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp size={18} style={{ color: 'var(--gold)' }} />
            <h2 className="text-h4">Market movers</h2>
          </div>
          <div className="flex flex-col divide-y" style={{ borderColor: 'var(--border)' }}>
            {loading
              ? [0, 1, 2].map((i) => <div key={i} className="py-3"><div className="skeleton h-5 w-full" /></div>)
              : markets.map((m) => (
                  <Link
                    key={m.id}
                    to={`/markets/${m.id}`}
                    className="flex items-center justify-between py-3 transition-colors hover:opacity-80"
                  >
                    <div>
                      <p className="text-sm font-medium">{m.name}</p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{m.district} · {m.distanceKm} km</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold tnum">{inrPerQ(m.lastPrice)}</p>
                      <p
                        className="text-xs tnum"
                        style={{ color: m.changePct >= 0 ? 'var(--emerald)' : 'var(--burgundy)' }}
                      >
                        {m.changePct >= 0 ? '+' : ''}{m.changePct}%
                      </p>
                    </div>
                  </Link>
                ))}
          </div>
        </div>

        <div className="card p-6">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sprout size={18} style={{ color: 'var(--emerald)' }} />
              <h2 className="text-h4">Your produce</h2>
            </div>
            <Link to="/produce" className="link-accent text-sm font-medium">Manage</Link>
          </div>
          <div className="space-y-3">
            {loading
              ? [0, 1].map((i) => <div key={i} className="skeleton h-16 w-full" />)
              : produce.map((p) => (
                  <div key={p.id} className="flex items-center gap-4 rounded-xl p-2" style={{ background: 'var(--midnight)' }}>
                    <img src={p.image} alt={p.cropName} className="h-14 w-14 flex-none rounded-lg object-cover" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium">{p.cropName}</p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{p.variety}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold tnum">{p.quantityQuintal} q</p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{p.harvestDate}</p>
                    </div>
                  </div>
                ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
