import React, { useEffect, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import Sidebar from './Sidebar';

const AppLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--midnight)' }}>
      {/* Desktop sidebar */}
      <aside
        className="fixed inset-y-0 left-0 z-40 hidden w-[264px] border-r lg:block"
        style={{ borderColor: 'var(--border)' }}
      >
        <Sidebar />
      </aside>

      {/* Mobile top bar */}
      <header
        className="sticky top-0 z-30 flex items-center justify-between border-b px-4 py-3 lg:hidden"
        style={{ backgroundColor: 'var(--sidebar)', borderColor: 'var(--border)' }}
      >
        <span className="font-display text-lg">KrishiX</span>
        <button
          onClick={() => setMobileOpen(true)}
          className="btn btn-ghost btn-sm"
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>
      </header>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="absolute inset-0"
            style={{ background: 'rgba(0,0,0,0.6)' }}
            onClick={() => setMobileOpen(false)}
          />
          <div className="absolute inset-y-0 left-0 w-[280px] animate-in">
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute right-3 top-3 z-10 btn btn-ghost btn-sm"
              aria-label="Close menu"
            >
              <X size={20} />
            </button>
            <Sidebar onNavigate={() => setMobileOpen(false)} />
          </div>
        </div>
      )}

      <main className="lg:pl-[264px]">
        <div className="mx-auto w-full max-w-content px-5 py-8 md:px-8 lg:px-10 lg:py-12">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default AppLayout;
