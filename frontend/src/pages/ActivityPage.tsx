import React, { useEffect, useState } from 'react';
import { Activity, Bookmark, Eye, Handshake, Sparkles } from 'lucide-react';
import { dataService, inr, type ActivityItem } from '../lib/mockData';
import { EmptyState, Eyebrow, Skeleton } from '../components/ui/primitives';

const kindMeta: Record<ActivityItem['kind'], { icon: React.ReactNode; tint: string }> = {
  offer: { icon: <Handshake size={16} />, tint: 'var(--indigo-soft)' },
  view: { icon: <Eye size={16} />, tint: 'rgba(245,241,232,0.06)' },
  save: { icon: <Bookmark size={16} />, tint: 'var(--gold-soft)' },
  analysis: { icon: <Sparkles size={16} />, tint: 'var(--violet-soft)' },
  deal: { icon: <Handshake size={16} />, tint: 'var(--emerald-soft)' },
};

const statusBadge: Record<ActivityItem['status'], string> = {
  completed: 'badge-emerald',
  pending: 'badge-gold',
  declined: 'badge-burgundy',
  info: 'badge-muted',
};

const ActivityPage: React.FC = () => {
  const [items, setItems] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dataService.getActivity().then((a) => {
      setItems(a);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-8">
      <header>
        <Eyebrow>Your history</Eyebrow>
        <h1 className="text-h1 font-display mt-2">Activity</h1>
        <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Offers, analyses and deals — most recent first.
        </p>
      </header>

      {loading ? (
        <div className="space-y-3">{[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full" />)}</div>
      ) : items.length === 0 ? (
        <EmptyState icon={<Activity size={24} />} title="No activity yet" message="Your offers and analyses will appear here." />
      ) : (
        <div className="card divide-y" style={{ borderColor: 'var(--border)' }}>
          {items.map((it) => {
            const meta = kindMeta[it.kind];
            return (
              <div key={it.id} className="flex items-center gap-4 p-4 md:p-5">
                <div
                  className="flex h-10 w-10 flex-none items-center justify-center rounded-xl"
                  style={{ background: meta.tint, color: 'var(--text-primary)' }}
                >
                  {meta.icon}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium">{it.title}</p>
                  <p className="mt-0.5 truncate text-xs" style={{ color: 'var(--text-muted)' }}>{it.detail}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  {it.amount != null && <p className="text-sm font-semibold tnum">{inr(it.amount)}</p>}
                  <div className="flex items-center gap-2">
                    <span className={`badge ${statusBadge[it.status]}`}>{it.status}</span>
                  </div>
                  <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{it.date}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ActivityPage;
