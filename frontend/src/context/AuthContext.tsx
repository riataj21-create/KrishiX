import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI, userAPI } from '../lib/api';

interface AuthUser {
  id: string;
  email: string;
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

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) { setUser(null); setLoading(false); return; }
    try {
      const u = await userAPI.getCurrentUser();
      setUser(u);
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refreshUser(); }, [refreshUser]);

  const login = async (email: string, password: string): Promise<AuthUser> => {
    const data = await authAPI.login(email, password);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('token_type', data.token_type);
    const u = await userAPI.getCurrentUser();
    setUser(u);
    return u;
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
