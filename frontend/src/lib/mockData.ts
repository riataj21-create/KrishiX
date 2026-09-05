// -----------------------------------------------------------------------------
// Isolated mock/service layer.
// The real backend contract lives in `lib/api.ts`. Everything here powers the
// features that do not yet have a live endpoint wired into the v0 preview, so
// the UI can be built and demoed. Swap these functions for `api.ts` calls once
// the corresponding backend routes are available — nothing else needs to change.
// -----------------------------------------------------------------------------

export type Feasibility = 'executable' | 'recoverable' | 'not_viable' | 'insufficient';

export interface CostBreakdown {
  transport: number;
  commission: number;
  labour: number;
  other: number;
}

export interface Produce {
  id: string;
  cropId: string;
  cropName: string;
  variety: string;
  image: string;
  quantityQuintal: number;
  harvestDate: string;
  location: string;
  gradeNote: string;
}

export interface PricePoint {
  date: string;
  price: number;
}

export interface Market {
  id: string;
  name: string;
  district: string;
  state: string;
  distanceKm: number;
  image: string;
  crops: string[];
  lastPrice: number;
  priceDate: string;
  changePct: number;
  arrivalsQuintal: number;
  history: PricePoint[];
}

export interface Opportunity {
  id: string;
  buyerName: string;
  buyerType: string;
  verified: boolean;
  cropName: string;
  cropImage: string;
  grossPrice: number; // ₹ per quintal offered
  quantityNeededQuintal: number;
  location: string;
  distanceKm: number;
  deadline: string;
  feasibility: Feasibility;
  netRealization: number; // ₹ per quintal in hand
  costs: CostBreakdown;
  reasons: string[];
  recovery?: string[];
}

export interface ActivityItem {
  id: string;
  kind: 'offer' | 'view' | 'save' | 'analysis' | 'deal';
  title: string;
  detail: string;
  date: string;
  amount?: number;
  status: 'completed' | 'pending' | 'declined' | 'info';
}

export interface AnalysisResult {
  cropName: string;
  quantityQuintal: number;
  bestMarketId: string;
  bestMarketName: string;
  netRealization: number;
  grossPrice: number;
  costs: CostBreakdown;
  confidence: number; // 0-100
  timing: 'sell_now' | 'hold';
  timingNote: string;
  factors: { label: string; value: string; tone: 'up' | 'down' | 'neutral' }[];
  alternatives: { marketId: string; marketName: string; net: number; distanceKm: number }[];
}

// -------------------------------- helpers ------------------------------------

export const inr = (n: number): string =>
  '₹' + Math.round(n).toLocaleString('en-IN');

export const inrPerQ = (n: number): string => inr(n) + '/q';

const wait = <T,>(data: T, ms = 550): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(data), ms));

const IMG = (n: string) => `/images/${n}`;

// -------------------------------- data ---------------------------------------

const markets: Market[] = [
  {
    id: 'mkt-nashik',
    name: 'Nashik APMC',
    district: 'Nashik',
    state: 'Maharashtra',
    distanceKm: 42,
    image: IMG('mandi.png'),
    crops: ['Tomato', 'Onion', 'Grapes'],
    lastPrice: 2450,
    priceDate: '2 Sep 2026',
    changePct: 6.2,
    arrivalsQuintal: 8200,
    history: [
      { date: '27 Aug', price: 2050 },
      { date: '28 Aug', price: 2120 },
      { date: '29 Aug', price: 2230 },
      { date: '30 Aug', price: 2180 },
      { date: '31 Aug', price: 2310 },
      { date: '1 Sep', price: 2380 },
      { date: '2 Sep', price: 2450 },
    ],
  },
  {
    id: 'mkt-pune',
    name: 'Pune Market Yard',
    district: 'Pune',
    state: 'Maharashtra',
    distanceKm: 96,
    image: IMG('market-land.png'),
    crops: ['Tomato', 'Chilli', 'Cotton'],
    lastPrice: 2610,
    priceDate: '2 Sep 2026',
    changePct: 3.1,
    arrivalsQuintal: 5400,
    history: [
      { date: '27 Aug', price: 2400 },
      { date: '28 Aug', price: 2450 },
      { date: '29 Aug', price: 2500 },
      { date: '30 Aug', price: 2480 },
      { date: '31 Aug', price: 2540 },
      { date: '1 Sep', price: 2580 },
      { date: '2 Sep', price: 2610 },
    ],
  },
  {
    id: 'mkt-solapur',
    name: 'Solapur APMC',
    district: 'Solapur',
    state: 'Maharashtra',
    distanceKm: 210,
    image: IMG('paddy.png'),
    crops: ['Tomato', 'Jowar', 'Cotton'],
    lastPrice: 2720,
    priceDate: '1 Sep 2026',
    changePct: -1.4,
    arrivalsQuintal: 3100,
    history: [
      { date: '26 Aug', price: 2800 },
      { date: '27 Aug', price: 2790 },
      { date: '28 Aug', price: 2770 },
      { date: '29 Aug', price: 2760 },
      { date: '30 Aug', price: 2740 },
      { date: '31 Aug', price: 2750 },
      { date: '1 Sep', price: 2720 },
    ],
  },
  {
    id: 'mkt-ahmednagar',
    name: 'Ahmednagar Mandi',
    district: 'Ahmednagar',
    state: 'Maharashtra',
    distanceKm: 74,
    image: IMG('cotton.png'),
    crops: ['Cotton', 'Tomato', 'Onion'],
    lastPrice: 2380,
    priceDate: '2 Sep 2026',
    changePct: 1.8,
    arrivalsQuintal: 4700,
    history: [
      { date: '27 Aug', price: 2280 },
      { date: '28 Aug', price: 2300 },
      { date: '29 Aug', price: 2320 },
      { date: '30 Aug', price: 2340 },
      { date: '31 Aug', price: 2350 },
      { date: '1 Sep', price: 2360 },
      { date: '2 Sep', price: 2380 },
    ],
  },
];

const produce: Produce[] = [
  {
    id: 'prod-1',
    cropId: 'tomato',
    cropName: 'Tomato',
    variety: 'Hybrid — Grade A',
    image: IMG('tomato.png'),
    quantityQuintal: 60,
    harvestDate: '28 Aug 2026',
    location: 'Sinnar, Nashik',
    gradeNote: 'Firm, uniform size, low blemish',
  },
  {
    id: 'prod-2',
    cropId: 'chilli',
    cropName: 'Chilli',
    variety: 'Guntur — dried',
    image: IMG('chilli.png'),
    quantityQuintal: 18,
    harvestDate: '20 Aug 2026',
    location: 'Sinnar, Nashik',
    gradeNote: 'Sun-dried, deep red, stemmed',
  },
];

const opportunities: Opportunity[] = [
  {
    id: 'opp-1',
    buyerName: 'Sahyadri Farms FPO',
    buyerType: 'Processor / Exporter',
    verified: true,
    cropName: 'Tomato',
    cropImage: IMG('tomato.png'),
    grossPrice: 2650,
    quantityNeededQuintal: 50,
    location: 'Nashik',
    distanceKm: 42,
    deadline: '6 Sep 2026',
    feasibility: 'executable',
    netRealization: 2412,
    costs: { transport: 148, commission: 66, labour: 18, other: 6 },
    reasons: [
      'Offer is 8% above the Nashik APMC modal price this week.',
      'Short 42 km haul keeps transport under ₹150/quintal.',
      'Verified buyer with on-time payment history.',
    ],
  },
  {
    id: 'opp-2',
    buyerName: 'Deccan Retail Co.',
    buyerType: 'Retail chain',
    verified: true,
    cropName: 'Tomato',
    cropImage: IMG('tomato.png'),
    grossPrice: 2780,
    quantityNeededQuintal: 40,
    location: 'Pune',
    distanceKm: 96,
    deadline: '5 Sep 2026',
    feasibility: 'recoverable',
    netRealization: 2360,
    costs: { transport: 336, commission: 70, labour: 20, other: 14 },
    reasons: [
      'Headline price is high, but 96 km transport eats ₹336/quintal.',
      'Net still beats your local mandi by ₹210 after costs.',
    ],
    recovery: [
      'Share a load with a neighbouring grower to halve transport to ~₹170/q.',
      'Negotiate buyer-paid freight — they have absorbed it before.',
    ],
  },
  {
    id: 'opp-3',
    buyerName: 'Krishna Exports',
    buyerType: 'Exporter',
    verified: false,
    cropName: 'Chilli',
    cropImage: IMG('chilli.png'),
    grossPrice: 14200,
    quantityNeededQuintal: 15,
    location: 'Solapur',
    distanceKm: 210,
    deadline: '9 Sep 2026',
    feasibility: 'not_viable',
    netRealization: 13160,
    costs: { transport: 880, commission: 142, labour: 12, other: 6 },
    reasons: [
      '210 km haul plus handling costs ₹1,040/quintal.',
      'Unverified buyer — payment terms unconfirmed.',
      'Net falls below what a verified buyer 40 km away offers.',
    ],
    recovery: [
      'Wait for a closer chilli buyer — 3 have posted within 60 km this month.',
    ],
  },
  {
    id: 'opp-4',
    buyerName: 'AgriConnect Mandi',
    buyerType: 'Aggregator',
    verified: true,
    cropName: 'Cotton',
    cropImage: IMG('cotton.png'),
    grossPrice: 7450,
    quantityNeededQuintal: 25,
    location: 'Ahmednagar',
    distanceKm: 74,
    deadline: '12 Sep 2026',
    feasibility: 'insufficient',
    netRealization: 0,
    costs: { transport: 0, commission: 0, labour: 0, other: 0 },
    reasons: [
      'No recent verified price prints for cotton at this mandi.',
      'We need at least 3 dated prices in the last 10 days to score this.',
    ],
  },
];

const activity: ActivityItem[] = [
  {
    id: 'act-1',
    kind: 'offer',
    title: 'Offer sent to Sahyadri Farms FPO',
    detail: 'Tomato · 50 q · ₹2,650/q',
    date: '2 Sep 2026',
    amount: 132500,
    status: 'pending',
  },
  {
    id: 'act-2',
    kind: 'analysis',
    title: 'Analysed Tomato — 60 q',
    detail: 'Best net: Nashik APMC · ₹2,412/q',
    date: '2 Sep 2026',
    status: 'info',
  },
  {
    id: 'act-3',
    kind: 'deal',
    title: 'Deal completed — Deccan Retail Co.',
    detail: 'Chilli · 12 q · ₹13,900/q',
    date: '24 Aug 2026',
    amount: 166800,
    status: 'completed',
  },
  {
    id: 'act-4',
    kind: 'save',
    title: 'Saved Pune Market Yard',
    detail: 'Tomato modal price up 3.1%',
    date: '22 Aug 2026',
    status: 'info',
  },
  {
    id: 'act-5',
    kind: 'view',
    title: 'Viewed opportunity — Krishna Exports',
    detail: 'Chilli · 15 q · flagged not viable',
    date: '21 Aug 2026',
    status: 'declined',
  },
];

// -------------------------------- service ------------------------------------

export const feasibilityMeta: Record<
  Feasibility,
  { label: string; badge: string; tone: string }
> = {
  executable: { label: 'Executable', badge: 'badge-emerald', tone: 'var(--emerald)' },
  recoverable: { label: 'Recoverable', badge: 'badge-gold', tone: 'var(--gold)' },
  not_viable: { label: 'Not viable', badge: 'badge-burgundy', tone: 'var(--burgundy)' },
  insufficient: { label: 'Not enough data', badge: 'badge-muted', tone: 'var(--text-muted)' },
};

export const dataService = {
  getMarkets: () => wait(markets),
  getMarket: (id: string) => wait(markets.find((m) => m.id === id) ?? null),
  getProduce: () => wait(produce),
  getOpportunities: () => wait(opportunities),
  getOpportunity: (id: string) => wait(opportunities.find((o) => o.id === id) ?? null),
  getActivity: () => wait(activity),
  getSavedMarkets: () => wait([markets[1], markets[2]]),
  getSavedOpportunities: () => wait([opportunities[0], opportunities[1]]),
  analyze: (cropName: string, quantityQuintal: number): Promise<AnalysisResult> =>
    wait(
      {
        cropName,
        quantityQuintal,
        bestMarketId: 'mkt-nashik',
        bestMarketName: 'Nashik APMC',
        netRealization: 2412,
        grossPrice: 2650,
        costs: { transport: 148, commission: 66, labour: 18, other: 6 },
        confidence: 82,
        timing: 'sell_now',
        timingNote:
          'Modal prices have risen 6.2% over the last week and arrivals are climbing — the near-term upside looks thin.',
        factors: [
          { label: 'Weekly price trend', value: '+6.2%', tone: 'up' },
          { label: 'Transport cost', value: inrPerQ(148), tone: 'neutral' },
          { label: 'Arrivals pressure', value: 'Rising', tone: 'down' },
          { label: 'Buyer verification', value: 'Verified', tone: 'up' },
        ],
        alternatives: [
          { marketId: 'mkt-pune', marketName: 'Pune Market Yard', net: 2360, distanceKm: 96 },
          { marketId: 'mkt-ahmednagar', marketName: 'Ahmednagar Mandi', net: 2210, distanceKm: 74 },
          { marketId: 'mkt-solapur', marketName: 'Solapur APMC', net: 2180, distanceKm: 210 },
        ],
      },
      1400,
    ),
};

export const CROPS = ['Tomato', 'Chilli', 'Cotton', 'Onion', 'Paddy', 'Jowar', 'Grapes'];
