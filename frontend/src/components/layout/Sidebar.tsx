import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Home,
  Sprout,
  Handshake,
  LineChart,
  Sparkles,
  Bookmark,
  Activity,
  LogOut,
  Wheat,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const primary = [
  { to: '/home', label: 'Home', icon: Home },
  { to: '/produce', label: 'My Produce', icon: Sprout },
  { to: '/opportunities', label: 'Opportunities', icon: Handshake },
  { to: '/markets', label: 'Markets', icon: LineChart },
  { to: '/analyzer', label: 'Analyzer', icon: Sparkles },
];

const secondary = [
  { to: '/saved', label: 'Saved', icon: Bookmark },
  { to: '/activity', label: 'Activity', icon: Activity },
];

const Brand: React.FC = () => (
  <div className="flex items-center gap-3 px-2">
    <div
      className="flex h-10 w-10 items-center justify-center rounded-xl"
      style={{ background: 'linear-gradient(135deg, var(--indigo), var(--violet))' }}
    >
      <Wheat size={20} className="text-white" />
    </div>
    <div>
      <p className="font-display text-lg leading-none tracking-tight">KrishiX</p>
      <p className="mt-1 text-[0.68rem] uppercase tracking-[0.16em]" style={{ color: 'var(--text-muted)' }}>
        Market Intelligence
      </p>
    </div>
  </div>
);

const NavItems: React.FC<{ items: typeof primary; onNavigate?: () => void }> = ({ items, onNavigate }) => (
  <nav className="flex flex-col gap-1">
    {items.map(({ to, label, icon: Icon }) => (
      <NavLink
        key={to}
        to={to}
        onClick={onNavigate}
        className={({ isActive }) => `nav-item ${isActive ? 'nav-item-active' : ''}`}
      >
        <Icon size={18} strokeWidth={1.8} />
        <span>{label}</span>
      </NavLink>
    ))}
  </nav>
);

const Sidebar: React.FC<{ onNavigate?: () => void }> = ({ onNavigate }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const initials = (user?.name || user?.email || 'K')
    .split(' ')
    .map((s) => s[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  return (
    <div className="flex h-full flex-col gap-8 p-5" style={{ backgroundColor: 'var(--sidebar)' }}>
      <div className="pt-2">
        <Brand />
      </div>

      <div className="flex flex-1 flex-col gap-7 overflow-y-auto">
        <NavItems items={primary} onNavigate={onNavigate} />
        <div>
          <p className="text-eyebrow mb-2 px-3">Library</p>
          <NavItems items={secondary} onNavigate={onNavigate} />
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <div className="hr" />
        <button
          onClick={() => { navigate('/profile'); onNavigate?.(); }}
          className="flex items-center gap-3 rounded-xl p-2 text-left transition-colors hover:bg-elevated"
        >
          <div
            className="flex h-9 w-9 flex-none items-center justify-center rounded-full text-sm font-semibold"
            style={{ background: 'var(--indigo-soft)', color: '#b3a5ff' }}
          >
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{user?.name || 'Farmer'}</p>
            <p className="truncate text-xs" style={{ color: 'var(--text-muted)' }}>{user?.email}</p>
          </div>
        </button>
        <button onClick={logout} className="nav-item w-full">
          <LogOut size={18} strokeWidth={1.8} />
          <span>Sign out</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
