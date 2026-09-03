/**
 * API Client - HTTP requests to KrishiX backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  signal?: AbortSignal;
}

async function makeRequest(
  endpoint: string,
  options: RequestOptions = {}
) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Add auth token if available
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    ...options,
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Clear token on auth error
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
      }
    }
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

// ============================================================================
// AUTH ENDPOINTS
// ============================================================================

export const authAPI = {
  register: (email: string, password: string) =>
    makeRequest("/api/auth/register", {
      method: "POST",
      body: { email, password },
    }),

  login: (email: string, password: string) =>
    makeRequest("/api/auth/login", {
      method: "POST",
      body: { email, password },
    }),

  logout: () =>
    makeRequest("/api/auth/logout", { method: "POST" }),
};

// ============================================================================
// USER ENDPOINTS
// ============================================================================

export const userAPI = {
  getCurrentUser: () => makeRequest("/api/users/me"),

  updateProfile: (email: string) =>
    makeRequest("/api/users/me", {
      method: "PUT",
      body: { email },
    }),
};

// ============================================================================
// FARMER PROFILE ENDPOINTS
// ============================================================================

export const farmerProfileAPI = {
  getProfile: () => makeRequest("/api/farmer-profile"),

  createProfile: (profileData: any) =>
    makeRequest("/api/farmer-profile", {
      method: "POST",
      body: profileData,
    }),

  updateProfile: (profileData: any) =>
    makeRequest("/api/farmer-profile", {
      method: "PUT",
      body: profileData,
    }),
};

// ============================================================================
// COMMODITY ENDPOINTS
// ============================================================================

export const commodityAPI = {
  listCommodities: (category?: string, limit: number = 20, offset: number = 0) => {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    params.append("limit", limit.toString());
    params.append("offset", offset.toString());
    return makeRequest(`/api/commodities?${params}`);
  },

  getCommodity: (id: string) => makeRequest(`/api/commodities/${id}`),
};

// ============================================================================
// MARKET ENDPOINTS
// ============================================================================

export const marketAPI = {
  listMarkets: (
    state: string,
    district?: string,
    limit: number = 20,
    offset: number = 0
  ) => {
    const params = new URLSearchParams();
    params.append("state", state);
    if (district) params.append("district", district);
    params.append("limit", limit.toString());
    params.append("offset", offset.toString());
    return makeRequest(`/api/markets?${params}`);
  },

  getMarket: (id: string) => makeRequest(`/api/markets/${id}`),
};

// ============================================================================
// MARKET PRICE ENDPOINTS
// ============================================================================

export const priceAPI = {
  getLatestPrices: (filters: {
    state?: string;
    district?: string;
    market_id?: string;
    commodity_id?: string;
    date?: string;
    limit?: number;
    offset?: number;
  }) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });
    return makeRequest(`/api/market-prices?${params}`);
  },

  comparePrices: (
    commodityId: string,
    state?: string,
    district?: string,
    date?: string
  ) => {
    const params = new URLSearchParams();
    params.append("commodity_id", commodityId);
    if (state) params.append("state", state);
    if (district) params.append("district", district);
    if (date) params.append("date", date);
    return makeRequest(`/api/market-prices/compare?${params}`);
  },

  getPriceHistory: (marketId: string, commodityId: string, days: number = 30) => {
    const params = new URLSearchParams();
    params.append("market_id", marketId);
    params.append("commodity_id", commodityId);
    params.append("days", days.toString());
    return makeRequest(`/api/market-prices/history?${params}`);
  },
};

// ============================================================================
// SAVED RESOURCES ENDPOINTS
// ============================================================================

export const savedAPI = {
  getSavedMarkets: (limit: number = 20, offset: number = 0) => {
    const params = new URLSearchParams();
    params.append("limit", limit.toString());
    params.append("offset", offset.toString());
    return makeRequest(`/api/saved-markets?${params}`);
  },

  saveMarket: (marketId: string) =>
    makeRequest(`/api/saved-markets/${marketId}`, { method: "POST" }),

  unsaveMarket: (marketId: string) =>
    makeRequest(`/api/saved-markets/${marketId}`, { method: "DELETE" }),

  getSavedCommodities: (limit: number = 20, offset: number = 0) => {
    const params = new URLSearchParams();
    params.append("limit", limit.toString());
    params.append("offset", offset.toString());
    return makeRequest(`/api/saved-commodities?${params}`);
  },

  saveCommodity: (commodityId: string) =>
    makeRequest(`/api/saved-commodities/${commodityId}`, { method: "POST" }),

  unsaveCommodity: (commodityId: string) =>
    makeRequest(`/api/saved-commodities/${commodityId}`, { method: "DELETE" }),
};
