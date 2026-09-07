import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Activity, BarChart3, Bookmark, ChevronRight, Leaf, LogOut, Map, Package, Search, Settings2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const primaryLinks = [
  { to: '/dashboard', label: 'Home', icon: BarChart3 },
  { to: '/produce', label: 'My produce', icon: Package },
  { to: '/opportunities', label: 'Opportunities', icon: Search },
  { to: '/markets', label: 'Markets', icon: Map },
  { to: '/sell', label: 'Analyzer', icon: Leaf },
];

const secondaryLinks = [
  { to: '/saved', label: 'Saved', icon: Bookmark },
  { to: '/activity', label: 'Activity', icon: Activity },
  { to: '/profile', label: 'Profile', icon: Settings2 },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="flex min-h-screen w-full bg-[#080b14] text-[#f5f1e8]">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-shrink-0 flex-col border-r border-white/5 bg-[#0d1020] p-6 lg:flex">
        <div className="flex items-center gap-3 px-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#5b4bdb] font-semibold text-white">K</div>
          <div><p className="font-serif text-lg font-semibold tracking-tight">KrishiX</p><p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#f0bf64]">Agricultural intelligence</p></div>
        </div>
        <p className="mt-10 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-[#928fa0]">Operations</p>
        <nav className="mt-2 space-y-1">
          {primaryLinks.map(({ to, label, icon: Icon }) => <NavItem key={to} to={to} label={label} icon={<Icon className="h-4 w-4" />} />)}
        </nav>
        <p className="mb-2 mt-8 px-3 text-[10px] font-bold uppercase tracking-[0.16em] text-[#928fa0]">Repository</p>
        <nav className="space-y-1">
          {secondaryLinks.map(({ to, label, icon: Icon }) => <NavItem key={to} to={to} label={label} icon={<Icon className="h-4 w-4" />} />)}
        </nav>
        <div className="mt-auto rounded-xl border border-white/[0.08] bg-[#15182a] p-3">
          <p className="truncate text-sm font-medium">{user?.email || 'Farmer account'}</p>
          <button className="mt-3 inline-flex items-center gap-2 text-xs text-[#a9a8b3] hover:text-white" onClick={() => { logout(); navigate('/login'); }}>
            <LogOut className="h-3.5 w-3.5" /> Log out
          </button>
        </div>
      </aside>
      <div className="min-w-0 flex-1 lg:ml-60">
        <div className="border-b border-white/10 bg-[#0d1020] px-5 py-3 lg:hidden">
          <div className="flex items-center gap-2"><div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#5b4bdb] font-semibold">K</div><span className="font-semibold">KrishiX</span></div>
          <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
            {[...primaryLinks, ...secondaryLinks].map(({ to, label }) => <NavLink key={to} to={to} className={({ isActive }) => `whitespace-nowrap rounded-full px-3 py-1.5 text-xs ${isActive ? 'bg-white/10 text-white' : 'text-[#a9a8b3]'}`}>{label}</NavLink>)}
          </div>
        </div>
        <main className="min-h-screen overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}

function NavItem({ to, label, icon }: { to: string; label: string; icon: React.ReactNode }) {
  return <NavLink to={to} className={({ isActive }) => `group flex items-center justify-between rounded-lg px-3 py-2 text-sm transition ${isActive ? 'bg-[#5b4bdb] font-medium text-[#e0dbff]' : 'text-[#c8c4d7] hover:bg-[#272a34] hover:text-white'}`}><span className="flex items-center gap-3">{icon}{label}</span><ChevronRight className="h-3.5 w-3.5 opacity-0 transition group-hover:opacity-60" /></NavLink>;
}
