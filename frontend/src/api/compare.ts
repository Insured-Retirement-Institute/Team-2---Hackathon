import { logRequest, logResponse } from "./logger";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";

export interface ProductOption {
  id: string;
  name: string;
  carrier: string;
  rate: string;
  term: string;
  premiumBonus?: string;
  surrenderPeriod: string;
  surrenderCharge?: string;
  freeWithdrawal: string;
  deathBenefit: string;
  guaranteedMinRate: string;
  riders?: string[];
  features?: string[];
  liquidity?: string;
  mvaPenalty?: string;
  licensingApproved?: boolean;
  licensingDetails?: string;
}

export interface ComparisonData {
  current: ProductOption;
  alternatives: ProductOption[];
  missingData: boolean;
}

export interface ComparisonResult {
  comparisonData: ComparisonData;
}

export interface VisualizationProduct {
  ID: string;
  productId: string;
  name: string;
  carrier: string;
  currentRate: number;
  guaranteedMinRate: number;
  surrenderYears: number;
  initialValue: number;
  premiumBonus?: number;
  incomeScore: number;
  growthScore: number;
  liquidityScore: number;
  protectionScore: number;
  projectedRates: Array<{
    year: number;
    conservativeRate: number;
    expectedRate: number;
    optimisticRate: number;
  }>;
  performanceData: Array<{
    year: number;
    value: number;
    income?: number;
  }>;
  features: Array<{
    name: string;
    startYear: number;
    endYear: number;
    category: "surrender" | "bonus" | "rider" | "guarantee";
  }>;
}

// Mock data
const mockComparison: ComparisonResult = {
  comparisonData: {
    current: {
      id: "current-1",
      name: "SecureChoice MYGA",
      carrier: "Integrity Life",
      rate: "3.80%",
      term: "5 years",
      surrenderPeriod: "7 years",
      freeWithdrawal: "10%",
      deathBenefit: "Return of premium",
      guaranteedMinRate: "1.50%",
    },
    alternatives: [
      {
        id: "alt-1",
        name: "FlexGrowth Plus MYGA",
        carrier: "Great American",
        rate: "4.25%",
        term: "7 years",
        premiumBonus: "3.0%",
        surrenderPeriod: "7 years",
        freeWithdrawal: "10%",
        deathBenefit: "Return of premium",
        guaranteedMinRate: "2.50%",
        licensingApproved: true,
      },
      {
        id: "alt-2",
        name: "Athene Performance Elite",
        carrier: "Athene",
        rate: "4.10%",
        term: "5 years",
        surrenderPeriod: "6 years",
        freeWithdrawal: "10%",
        deathBenefit: "Account value",
        guaranteedMinRate: "2.00%",
        licensingApproved: true,
      },
      {
        id: "alt-3",
        name: "Nationwide Peak",
        carrier: "Nationwide",
        rate: "3.95%",
        term: "5 years",
        surrenderPeriod: "5 years",
        freeWithdrawal: "10%",
        deathBenefit: "Account value",
        guaranteedMinRate: "2.25%",
        licensingApproved: false,
        licensingDetails: "Appointment required",
      },
    ],
    missingData: false,
  },
};

const mockVisualizationProducts: VisualizationProduct[] = [
  {
    ID: "viz-1",
    productId: "PROD-CURRENT",
    name: "SecureChoice MYGA (Current)",
    carrier: "Integrity Life",
    currentRate: 3.8,
    guaranteedMinRate: 1.5,
    surrenderYears: 7,
    initialValue: 180000,
    incomeScore: 65,
    growthScore: 58,
    liquidityScore: 55,
    protectionScore: 72,
    projectedRates: [
      { year: 1, conservativeRate: 1.5, expectedRate: 3.8, optimisticRate: 4.2 },
      { year: 2, conservativeRate: 1.5, expectedRate: 3.5, optimisticRate: 4.0 },
      { year: 3, conservativeRate: 1.5, expectedRate: 3.2, optimisticRate: 3.8 },
      { year: 4, conservativeRate: 1.5, expectedRate: 3.0, optimisticRate: 3.6 },
      { year: 5, conservativeRate: 1.5, expectedRate: 2.8, optimisticRate: 3.4 },
    ],
    performanceData: [
      { year: 0, value: 180000 },
      { year: 1, value: 186840 },
      { year: 2, value: 193380 },
      { year: 3, value: 199560 },
      { year: 4, value: 205548 },
      { year: 5, value: 211303 },
    ],
    features: [
      { name: "Surrender Charge", startYear: 1, endYear: 7, category: "surrender" },
      { name: "Rate Guarantee", startYear: 1, endYear: 5, category: "guarantee" },
    ],
  },
  {
    ID: "viz-2",
    productId: "PROD-FLEX",
    name: "FlexGrowth Plus MYGA",
    carrier: "Great American",
    currentRate: 4.25,
    guaranteedMinRate: 2.5,
    surrenderYears: 7,
    initialValue: 180000,
    premiumBonus: 3.0,
    incomeScore: 78,
    growthScore: 85,
    liquidityScore: 60,
    protectionScore: 88,
    projectedRates: [
      { year: 1, conservativeRate: 2.5, expectedRate: 4.25, optimisticRate: 4.8 },
      { year: 2, conservativeRate: 2.5, expectedRate: 4.0, optimisticRate: 4.6 },
      { year: 3, conservativeRate: 2.5, expectedRate: 3.8, optimisticRate: 4.4 },
      { year: 4, conservativeRate: 2.5, expectedRate: 3.6, optimisticRate: 4.2 },
      { year: 5, conservativeRate: 2.5, expectedRate: 3.4, optimisticRate: 4.0 },
    ],
    performanceData: [
      { year: 0, value: 180000 },
      { year: 1, value: 193050 },
      { year: 2, value: 200772 },
      { year: 3, value: 208401 },
      { year: 4, value: 215903 },
      { year: 5, value: 223243 },
    ],
    features: [
      { name: "Premium Bonus", startYear: 1, endYear: 1, category: "bonus" },
      { name: "Surrender Charge", startYear: 1, endYear: 7, category: "surrender" },
      { name: "Rate Guarantee", startYear: 1, endYear: 7, category: "guarantee" },
    ],
  },
];

export async function runComparison(alertId: string): Promise<ComparisonResult> {
  logRequest(`POST /api/alerts/${alertId}/compare`);

  if (USE_MOCKS) {
    return new Promise((resolve) => {
      setTimeout(() => {
        logResponse(`POST /api/alerts/${alertId}/compare (mock)`, mockComparison);
        resolve(mockComparison);
      }, 800);
    });
  }

  const res = await fetch(`${API_BASE_URL}/alerts/${alertId}/compare`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed: ${res.statusText}`);
  const data = await res.json();
  logResponse(`POST /api/alerts/${alertId}/compare`, data);
  return data;
}

export async function recompareWithProducts(
  alertId: string,
  selectedProducts: ProductOption[]
): Promise<ComparisonResult> {
  logRequest(`POST /api/alerts/${alertId}/compare/products`);

  if (USE_MOCKS) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const result: ComparisonResult = {
          comparisonData: {
            current: mockComparison.comparisonData.current,
            alternatives: selectedProducts,
            missingData: false,
          },
        };
        logResponse(`POST /api/alerts/${alertId}/compare/products (mock)`, result);
        resolve(result);
      }, 800);
    });
  }

  const res = await fetch(`${API_BASE_URL}/alerts/${alertId}/compare/products`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selectedProducts }),
  });
  if (!res.ok) throw new Error(`Failed: ${res.statusText}`);
  const data = await res.json();
  logResponse(`POST /api/alerts/${alertId}/compare/products`, data);
  return data;
}

export async function getVisualizationProducts(): Promise<VisualizationProduct[]> {
  logRequest("GET /passthrough/visualization-products");

  if (USE_MOCKS) {
    return new Promise((resolve) => {
      setTimeout(() => {
        logResponse("GET /passthrough/visualization-products (mock)", mockVisualizationProducts);
        resolve(mockVisualizationProducts);
      }, 300);
    });
  }

  const res = await fetch(`${API_BASE_URL.replace("/api", "")}/passthrough/visualization-products`);
  if (!res.ok) throw new Error(`Failed: ${res.statusText}`);
  const data = await res.json();
  logResponse("GET /passthrough/visualization-products", data);
  return data;
}
