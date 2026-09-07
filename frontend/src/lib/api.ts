/**
 * KrishiX API Client
 * All requests use relative /api/* paths — Vite proxies them to the backend.
 * No env var baking. Works identically in Docker and local dev.
 */

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
}

export interface Commodity {
  id: string;
  name: string;
  category?: string | null;
  unit: string;
}

export interface Market {
  id: string;
  name: string;
  state: string;
  district: string;
  latitude?: number | null;
  longitude?: number | null;
  market_type?: string | null;
}

export interface FarmerLot {
  id: string;
  commodity_id: string;
  commodity_name?: string | null;
  quantity: number;
  quantity_kg?: number;
  unit: string;
  state: string;
  district: string;
  village?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  quality_grade?: string | null;
  quality_status?: string | null;
  quality_notes?: string | null;
  available_from: string;
  sell_by: string;
  minimum_price?: number | null;
  max_payment_days: number;
  preferred_payment_method?: string | null;
  transport_preference?: string | null;
  max_transport_budget?: number | null;
  status: string;
}

export interface Opportunity {
  id: string;
  lot_id: string;
  opportunity_type: string;
  feasibility_decision: 'EXECUTABLE' | 'RECOVERABLE' | 'NOT_VIABLE' | 'INSUFFICIENT_DATA' | string;
  blocking_constraints: string[];
  opportunity_gaps: Array<{ explanation?: string; constraint?: string; [key: string]: unknown }>;
  minimum_viable_changes: Array<{ description?: string; feasible?: boolean; [key: string]: unknown }>;
  offered_price?: number | null;
  estimated_net_realization?: number | null;
  source_type: string;
  data_quality?: string | null;
  rank?: number | null;
  confidence_score?: number | null;
  explanation?: string | null;
  title?: string | null;
  warnings?: string[];
  price_kind?: string;
}

export interface Buyer {
  id: string;
  name: string;
  buyer_type?: string;
  commodity_name?: string;
  state?: string;
  district?: string;
  quality_grade?: string;
  payment_terms?: string;
  rating?: number | null;
  is_verified?: boolean;
  whatsapp_link?: string | null;
  price_premium_pct?: number;
}

export interface FarmerProfile {
  id: string;
  user_id: string;
  full_name: string;
  phone?: string | null;
  state: string;
  district: string;
  village?: string | null;
  postal_code?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  bio?: string | null;
}

export interface TransactionEvent {
  id: string;
  event_type: string;
  event_data?: string | null;
  created_at: string;
}

export interface Transaction {
  id: string;
  offer_id: string;
  lot_id: string;
  buyer_id: string;
  agreed_price_per_quintal: number;
  agreed_quantity: number;
  agreed_payment_days: number;
  payment_status: string;
  status: string;
  is_disputed: boolean;
  created_at: string;
  updated_at: string;
  events: TransactionEvent[];
  payment?: {
    payment_status: string;
    payment_amount: number;
    payment_due_date: string;
    buyer_reported_paid_at?: string | null;
    farmer_confirmed_at?: string | null;
    is_protected: boolean;
    disclaimer?: string;
  } | null;
  disclaimer?: string;
}

async function makeRequest<T = unknown>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const token = localStorage.getItem("access_token");
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const response = await fetch(endpoint, {
    ...options,
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user");
    }
    let message = `${response.status}`;
    try {
      const err = await response.json();
      message = err.detail || err.message || message;
    } catch {
      message = response.statusText || message;
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

// ── Auth ────────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (email: string, password: string, role: 'farmer' | 'buyer' = 'farmer') =>
    makeRequest("/api/auth/register", { method: "POST", body: { email, password, role } }),
  login: (email: string, password: string) =>
    makeRequest<{ access_token: string; token_type: string; expires_in?: number }>("/api/auth/login", {
      method: "POST", body: { email, password },
    }),
  logout: () => makeRequest("/api/auth/logout", { method: "POST" }),
};

// ── Users ───────────────────────────────────────────────────────────────────
export const userAPI = {
  getCurrentUser: () => makeRequest<{ id: string; email: string; role: 'farmer' | 'buyer' }>("/api/users/me"),
  changePassword: (current_password: string, new_password: string) =>
    makeRequest("/api/users/me/password", {
      method: "PUT", body: { current_password, new_password },
    }),
};

// ── Farmer Profile ──────────────────────────────────────────────────────────
export const farmerProfileAPI = {
  getProfile: () => makeRequest<FarmerProfile>("/api/farmer-profile"),
  createProfile: (data: unknown) =>
    makeRequest("/api/farmer-profile", { method: "POST", body: data }),
  updateProfile: (data: unknown) =>
    makeRequest("/api/farmer-profile", { method: "PUT", body: data }),
};

// ── Commodities ─────────────────────────────────────────────────────────────
export const commodityAPI = {
  listCommodities: (category?: string, limit = 20, offset = 0) => {
    const p = new URLSearchParams();
    if (category) p.append("category", category);
    p.append("limit", String(limit));
    p.append("offset", String(offset));
    return makeRequest<{ total: number; items: Commodity[] }>(`/api/commodities?${p}`);
  },
  getCommodity: (id: string) => makeRequest<Commodity>(`/api/commodities/${id}`),
};

// ── Markets ─────────────────────────────────────────────────────────────────
export const marketAPI = {
  listMarkets: (state: string, district?: string, limit = 20, offset = 0) => {
    const p = new URLSearchParams({ state });
    if (district) p.append("district", district);
    p.append("limit", String(limit));
    p.append("offset", String(offset));
    return makeRequest<{ total: number; items: Market[] }>(`/api/markets?${p}`);
  },
  getMarket: (id: string) => makeRequest<Market>(`/api/markets/${id}`),
};

// ── Market Prices ───────────────────────────────────────────────────────────
export const priceAPI = {
  getLatestPrices: (filters: {
    state?: string; district?: string; market_id?: string;
    commodity_id?: string; date?: string; limit?: number; offset?: number;
  }) => {
    const p = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => { if (v != null) p.append(k, String(v)); });
    return makeRequest<{ total: number; items: any[] }>(`/api/market-prices?${p}`);
  },
  comparePrices: (commodityId: string, state?: string, district?: string, date?: string) => {
    const p = new URLSearchParams({ commodity_id: commodityId });
    if (state) p.append("state", state);
    if (district) p.append("district", district);
    if (date) p.append("date", date);
    return makeRequest<any>(`/api/market-prices/compare?${p}`);
  },
  getPriceHistory: (marketId: string, commodityId: string, days = 30) => {
    const p = new URLSearchParams({ market_id: marketId, commodity_id: commodityId, days: String(days) });
    return makeRequest<any>(`/api/market-prices/history?${p}`);
  },
};

// ── Selling Decision ────────────────────────────────────────────────────────
export const decisionAPI = {
  getDecision: (params: {
    commodity_id: string; quantity_quintal: number;
    farmer_lat?: number; farmer_lon?: number; state?: string; district?: string;
  }) => {
    const p = new URLSearchParams({
      commodity_id: params.commodity_id,
      quantity_quintal: String(params.quantity_quintal),
    });
    if (params.farmer_lat != null) p.append("farmer_lat", String(params.farmer_lat));
    if (params.farmer_lon != null) p.append("farmer_lon", String(params.farmer_lon));
    if (params.state) p.append("state", params.state);
    if (params.district) p.append("district", params.district);
    return makeRequest<any>(`/api/selling-decision?${p}`);
  },
};

// ── Lots and feasibility opportunities ───────────────────────────────────────
export const lotAPI = {
  listLots: () => makeRequest<{ total: number; items: FarmerLot[] }>("/api/lots"),
  getLot: (lotId: string) => makeRequest<FarmerLot>(`/api/lots/${lotId}`),
  createLot: (data: Omit<FarmerLot, "id" | "status" | "commodity_name" | "quantity_kg">) =>
    makeRequest<FarmerLot>("/api/lots", { method: "POST", body: data }),
  getOpportunities: (lotId: string) =>
    makeRequest<{ lot_id: string; items: Opportunity[]; recommendation?: string; data_caveat?: string }>(
      `/api/lots/${lotId}/opportunities`,
    ),
  analyzeOpportunities: (lotId: string, farmerPriority = "maximize_realization") =>
    makeRequest<{ lot_id: string; items: Opportunity[]; recommendation: string; data_caveat: string }>(
      `/api/lots/${lotId}/opportunities/analyze?farmer_priority=${encodeURIComponent(farmerPriority)}`,
      { method: "POST" },
    ),
  getOpportunity: (opportunityId: string) => makeRequest<Opportunity>(`/api/opportunities/${opportunityId}`),
  offerFromOpportunity: (opportunityId: string) =>
    makeRequest<{ id: string; status: string }>(`/api/opportunities/${opportunityId}/offer`, { method: "POST" }),
};

// ── Offers, transactions, and truthful payment status ───────────────────────
export const transactionAPI = {
  listTransactions: () => makeRequest<{ items: Transaction[]; disclaimer?: string }>("/api/transactions"),
  getTransaction: (transactionId: string) => makeRequest<Transaction>(`/api/transactions/${transactionId}`),
  advance: (transactionId: string) => makeRequest<Transaction>(`/api/transactions/${transactionId}/advance`, { method: "POST" }),
  reportPayment: (transactionId: string, payment_reference?: string) =>
    makeRequest<Transaction>(`/api/transactions/${transactionId}/payment/report`, { method: "POST", body: { payment_reference } }),
  confirmPayment: (transactionId: string, confirmed: boolean, notes?: string) =>
    makeRequest<Transaction>(`/api/transactions/${transactionId}/payment/confirm`, { method: "POST", body: { confirmed, notes } }),
};

// ── Buyers ──────────────────────────────────────────────────────────────────
export const buyerAPI = {
  listBuyers: (commodity?: string, state?: string) => {
    const p = new URLSearchParams();
    if (commodity) p.append("commodity", commodity);
    if (state) p.append("state", state);
    return makeRequest<{ total: number; items: Buyer[]; data_status?: string; data_note?: string; empty_state_message?: string }>(`/api/buyers?${p}`);
  },
};

// ── Weather ──────────────────────────────────────────────────────────────────
export const weatherAPI = {
  getWeather: (lat: number, lon: number) =>
    makeRequest<{
      data_status: string;
      current?: { temperature_c?: number; humidity_pct?: number; wind_speed_kmh?: number };
      transport_risk?: { risk_level: string; risk_factors: string[]; sell_signal: string };
      message?: string;
    }>(`/api/weather?lat=${lat}&lon=${lon}`),
};

// ── Saved ───────────────────────────────────────────────────────────────────
export const savedAPI = {
  getSavedMarkets: (limit = 20, offset = 0) => {
    const p = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    return makeRequest<{ total: number; items: any[] }>(`/api/saved-markets?${p}`);
  },
  saveMarket: (marketId: string) =>
    makeRequest(`/api/saved-markets/${marketId}`, { method: "POST" }),
  unsaveMarket: (marketId: string) =>
    makeRequest(`/api/saved-markets/${marketId}`, { method: "DELETE" }),
  getSavedCommodities: (limit = 20, offset = 0) => {
    const p = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    return makeRequest<{ total: number; items: any[] }>(`/api/saved-commodities?${p}`);
  },
  saveCommodity: (commodityId: string) =>
    makeRequest(`/api/saved-commodities/${commodityId}`, { method: "POST" }),
  unsaveCommodity: (commodityId: string) =>
    makeRequest(`/api/saved-commodities/${commodityId}`, { method: "DELETE" }),
};
