import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI, userAPI } from '../lib/api';

interface AuthUser {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<AuthUser>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// In the v0 preview the FastAPI backend is not reachable. When a request fails
// with a network error we fall back to a local demo session so the frontend can
// be exercised. The real backend (lib/api.ts) always remains the primary path —
// this only triggers when fetch itself cannot connect.
const isNetworkError = (err: unknown) =>
  err instanceof TypeError || (err instanceof Error && /failed to fetch|networkerror/i.test(err.message));

const nameFromEmail = (email: string) =>
  email.split('@')[0].replace(/[._-]+/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

const DEMO_TOKEN = 'demo-session';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) { setUser(null); setLoading(false); return; }

    if (token === DEMO_TOKEN) {
      const stored = localStorage.getItem('user');
      setUser(stored ? JSON.parse(stored) : null);
      setLoading(false);
      return;
    }

    try {
      const u = await userAPI.getCurrentUser();
      setUser(u);
    } catch (err) {
      if (isNetworkError(err)) {
        const stored = localStorage.getItem('user');
        if (stored) { setUser(JSON.parse(stored)); setLoading(false); return; }
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refreshUser(); }, [refreshUser]);

  const login = async (email: string, password: string): Promise<AuthUser> => {
    try {
      const data = await authAPI.login(email, password);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('token_type', data.token_type);
      const u = await userAPI.getCurrentUser();
      localStorage.setItem('user', JSON.stringify(u));
      setUser(u);
      return u;
    } catch (err) {
      if (isNetworkError(err)) {
        const demo: AuthUser = { id: 'demo', email, name: nameFromEmail(email) };
        localStorage.setItem('access_token', DEMO_TOKEN);
        localStorage.setItem('token_type', 'bearer');
        localStorage.setItem('user', JSON.stringify(demo));
        setUser(demo);
        return demo;
      }
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, isAuthenticated: !!user, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
