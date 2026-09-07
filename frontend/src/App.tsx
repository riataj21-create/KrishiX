import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { RoleGuard } from './components/layout/RoleGuard';
import AppShell from './components/layout/AppShell';

// ── Auth pages ──────────────────────────────────────────────────────────────
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';

// ── Farmer pages ────────────────────────────────────────────────────────────
import DashboardPage from './pages/farmer/DashboardPage';
import DecisionPage from './pages/farmer/DecisionPage';
import SearchPage from './pages/farmer/SearchPage';
import ComparisonPage from './pages/farmer/ComparisonPage';
import TrendsPage from './pages/farmer/TrendsPage';
import SavedPage from './pages/farmer/SavedPage';
import ProfilePage from './pages/farmer/ProfilePage';
import BuyersPage from './pages/farmer/BuyersPage';
import ProducePage from './pages/farmer/ProducePage';
import OpportunitiesPage from './pages/farmer/OpportunitiesPage';
import OpportunityDetailPage from './pages/farmer/OpportunityDetailPage';
import ActivityPage from './pages/farmer/ActivityPage';

// ── Buyer pages ─────────────────────────────────────────────────────────────
import BuyerDashboard from './pages/buyer/BuyerDashboard';

// ── Landing ──────────────────────────────────────────────────────────────────
import LandingPage from './pages/LandingPage';

/**
 * Root redirect — sends authenticated users to their role-specific portal.
 * Pattern from TechVision RootRedirect.
 */
function RootRedirect() {
  const { user, loading, isAuthenticated } = useAuth();
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role === 'buyer') return <Navigate to="/buyer/dashboard" replace />;
  return <Navigate to="/dashboard" replace />;
}

function FarmerPage({ children }: { children: React.ReactNode }) {
  return <RoleGuard><AppShell>{children}</AppShell></RoleGuard>;
}

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Routes>
            {/* Public */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Root redirect after login */}
            <Route path="/home" element={<RootRedirect />} />

            {/* Farmer portal */}
            <Route path="/dashboard" element={<FarmerPage><DashboardPage /></FarmerPage>} />
            <Route path="/produce" element={<FarmerPage><ProducePage /></FarmerPage>} />
            <Route path="/sell" element={<FarmerPage><DecisionPage /></FarmerPage>} />
            <Route path="/markets" element={<FarmerPage><SearchPage /></FarmerPage>} />
            <Route path="/compare" element={<FarmerPage><ComparisonPage /></FarmerPage>} />
            <Route path="/trends" element={<FarmerPage><TrendsPage /></FarmerPage>} />
            <Route path="/saved" element={<FarmerPage><SavedPage /></FarmerPage>} />
            <Route path="/buyers" element={<FarmerPage><BuyersPage /></FarmerPage>} />
            <Route path="/profile" element={<FarmerPage><ProfilePage /></FarmerPage>} />
            <Route path="/activity" element={<FarmerPage><ActivityPage /></FarmerPage>} />
            <Route path="/opportunities" element={<FarmerPage><OpportunitiesPage /></FarmerPage>} />
            <Route path="/opportunities/:lotId" element={<FarmerPage><OpportunitiesPage /></FarmerPage>} />
            <Route path="/opportunities/detail/:opportunityId" element={<FarmerPage><OpportunityDetailPage /></FarmerPage>} />

            {/* Buyer portal */}
            <Route path="/buyer/dashboard" element={<RoleGuard><AppShell><BuyerDashboard /></AppShell></RoleGuard>} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
