import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { RoleGuard } from './components/layout/RoleGuard';

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
            <Route path="/dashboard" element={<RoleGuard><DashboardPage /></RoleGuard>} />
            <Route path="/sell" element={<RoleGuard><DecisionPage /></RoleGuard>} />
            <Route path="/markets" element={<RoleGuard><SearchPage /></RoleGuard>} />
            <Route path="/compare" element={<RoleGuard><ComparisonPage /></RoleGuard>} />
            <Route path="/trends" element={<RoleGuard><TrendsPage /></RoleGuard>} />
            <Route path="/saved" element={<RoleGuard><SavedPage /></RoleGuard>} />
            <Route path="/buyers" element={<RoleGuard><BuyersPage /></RoleGuard>} />
            <Route path="/profile" element={<RoleGuard><ProfilePage /></RoleGuard>} />

            {/* Buyer portal */}
            <Route path="/buyer/dashboard" element={<RoleGuard><BuyerDashboard /></RoleGuard>} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
