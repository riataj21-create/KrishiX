import React from 'react';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { feasibilityMeta, inr, type Feasibility, type PricePoint } from '../../lib/mockData';

export const Eyebrow: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <span className={`text-eyebrow ${className}`}>{children}</span>
);

export const FeasibilityBadge: React.FC<{ status: Feasibility }> = ({ status }) => {
  const meta = feasibilityMeta[status];
  return (
    <span className={`badge ${meta.badge}`}>
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: 'currentColor' }} aria-hidden />
      {meta.label}
    </span>
  );
};

export const Stat: React.FC<{ label: string; value: string; sub?: string; tone?: 'up' | 'down' | 'neutral' }> = ({
  label,
  value,
  sub,
  tone = 'neutral',
}) => {
  const toneColor = tone === 'up' ? 'text-emerald' : tone === 'down' ? 'text-burgundy' : '';
  return (
    <div className="card p-5">
      <p className="text-eyebrow mb-2">{label}</p>
      <p className="text-h2 font-display tnum leading-none">{value}</p>
      {sub && <p className={`mt-2 text-sm tnum ${toneColor}`} style={{ color: 'var(--text-secondary)' }}>{sub}</p>}
    </div>
  );
};

export const EmptyState: React.FC<{
  title: string;
  message: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}> = ({ title, message, icon, action }) => (
  <div className="card flex flex-col items-center justify-center px-6 py-16 text-center">
    {icon && (
      <div
        className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl"
        style={{ background: 'var(--indigo-soft)', color: '#b3a5ff' }}
      >
        {icon}
      </div>
    )}
    <h3 className="text-h3 font-display">{title}</h3>
    <p className="mt-2 max-w-sm text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
      {message}
    </p>
    {action && <div className="mt-6">{action}</div>}
  </div>
);

export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`skeleton ${className}`} />
);

export const CardSkeleton: React.FC = () => (
  <div className="card overflow-hidden">
    <Skeleton className="h-40 w-full rounded-none" />
    <div className="space-y-3 p-5">
      <Skeleton className="h-4 w-2/3" />
      <Skeleton className="h-3 w-1/2" />
      <Skeleton className="h-8 w-full" />
    </div>
  </div>
);

export const PriceChart: React.FC<{ data: PricePoint[]; height?: number }> = ({ data, height = 220 }) => (
  <ResponsiveContainer width="100%" height={height}>
    <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: -18 }}>
      <defs>
        <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.45} />
          <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
        </linearGradient>
      </defs>
      <XAxis
        dataKey="date"
        tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
        axisLine={false}
        tickLine={false}
      />
      <YAxis
        tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
        axisLine={false}
        tickLine={false}
        width={54}
        tickFormatter={(v) => inr(v as number)}
      />
      <Tooltip
        cursor={{ stroke: 'var(--border-strong)' }}
        contentStyle={{
          background: 'var(--raised)',
          border: '1px solid var(--border-strong)',
          borderRadius: 12,
          color: 'var(--text-primary)',
          fontSize: 13,
        }}
        formatter={(v: number) => [inr(v) + '/q', 'Modal price']}
      />
      <Area
        type="monotone"
        dataKey="price"
        stroke="#8b5cf6"
        strokeWidth={2.5}
        fill="url(#priceFill)"
        dot={false}
        activeDot={{ r: 4, fill: '#8b5cf6' }}
      />
    </AreaChart>
  </ResponsiveContainer>
);

export const Spinner: React.FC<{ className?: string }> = ({ className = '' }) => (
  <svg className={`spin ${className}`} width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
    <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
  </svg>
);
