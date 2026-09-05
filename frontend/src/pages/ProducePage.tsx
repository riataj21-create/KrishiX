import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Sprout, MapPin, Calendar, Search } from 'lucide-react';
import { dataService, type Produce } from '../lib/mockData';
import { CardSkeleton, EmptyState, Eyebrow } from '../components/ui/primitives';

const ProducePage: React.FC = () => {
  const [produce, setProduce] = useState<Produce[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataService.getProduce().then((p) => {
      setProduce(p);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <Eyebrow>Your listings</Eyebrow>
          <h1 className="text-h1 font-display mt-2">My Produce</h1>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            List what you have. We match it against every buyer and mandi.
          </p>
        </div>
        <Link to="/produce/add" className="btn btn-primary">
          <Plus size={18} /> Add produce
        </Link>
      </header>

      {loading ? (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => <CardSkeleton key={i} />)}
        </div>
      ) : produce.length === 0 ? (
        <EmptyState
          icon={<Sprout size={24} />}
          title="No produce listed yet"
          message="Add your first crop to start seeing buyers ranked by the real net price you would receive."
          action={<Link to="/produce/add" className="btn btn-primary"><Plus size={18} /> Add produce</Link>}
        />
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {produce.map((p) => (
            <div key={p.id} className="card card-hover overflow-hidden">
              <div className="relative h-44">
                <img src={p.image} alt={p.cropName} className="h-full w-full object-cover" />
                <span className="badge badge-violet absolute left-3 top-3">{p.quantityQuintal} quintal</span>
              </div>
              <div className="p-5">
                <h3 className="text-h4">{p.cropName}</h3>
                <p className="mt-0.5 text-sm" style={{ color: 'var(--text-secondary)' }}>{p.variety}</p>
                <div className="mt-4 space-y-2 text-xs" style={{ color: 'var(--text-muted)' }}>
                  <p className="flex items-center gap-2"><MapPin size={13} /> {p.location}</p>
                  <p className="flex items-center gap-2"><Calendar size={13} /> Harvested {p.harvestDate}</p>
                </div>
                <div className="mt-4 flex items-center justify-between border-t pt-4" style={{ borderColor: 'var(--border)' }}>
                  <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{p.gradeNote}</p>
                  <Link to="/opportunities" className="link-accent inline-flex items-center gap-1 text-xs font-medium">
                    <Search size={13} /> Find buyers
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProducePage;
