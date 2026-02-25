export type RenewalAlert = {
  id: string;
  clientId: string;
  policyId: string;
  clientName: string;
  carrier: string;
  renewalDate: string;
  daysUntilRenewal: number;
  currentRate: string;
  renewalRate: string;
  currentValue: string;
  isMinRate: boolean;
  priority: "high" | "medium" | "low";
  hasDataException: boolean;
  missingFields?: string[];
  status: "pending" | "reviewed" | "snoozed" | "dismissed";
  alertType:
    | "replacement_recommended"
    | "replacement_opportunity"
    | "missing_info"
    | "suitability_review"
    | "income_planning";
  alertTypes?: (
    | "replacement_recommended"
    | "replacement_opportunity"
    | "missing_info"
    | "suitability_review"
    | "income_planning"
  )[];
  alertDescription: string;
};

export type DashboardStats = {
  total: number;
  high: number;
  urgent: number;
  totalValue: number;
};
