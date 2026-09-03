/**
 * useAuth Hook
 * Manages authentication state and user data
 */

import { useState, useEffect, useCallback } from "react";

interface AuthUser {
  id: string;
  email: string;
}

interface UseAuthReturn {
  user: AuthUser | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  logout: () => void;
  setToken: (token: string) => void;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load auth state on mount
  useEffect(() => {
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) {
      setToken(storedToken);
      // Could load user data here if needed
    }
    setIsLoading(false);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    setToken(null);
    setUser(null);
  }, []);

  const handleSetToken = useCallback((newToken: string) => {
    localStorage.setItem("access_token", newToken);
    setToken(newToken);
  }, []);

  return {
    user,
    token,
    isLoading,
    isAuthenticated: !!token,
    logout,
    setToken: handleSetToken,
  };
}
