export type VisualizationProduct = {
  ID: string;
  productId: string;
  name: string;
  carrier: string;
  currentRate: number;
  guaranteedMinRate: number;
  surrenderYears: number;
  initialValue: number;
  premiumBonus?: number | null;
  incomeScore: number;
  growthScore: number;
  liquidityScore: number;
  protectionScore: number;
  projectedRates: {
    year: number;
    conservativeRate: number;
    expectedRate: number;
    optimisticRate: number;
  }[];
  performanceData: { year: number; value: number; income?: number }[];
  features: {
    name: string;
    startYear: number;
    endYear: number;
    category: "surrender" | "bonus" | "rider" | "guarantee";
  }[];
};

export type PolicyFeature = {
  name: string;
  description: string;
  included: boolean;
  type: "feature" | "benefit" | "rider" | "limitation";
};

export type PolicyFeaturesData = {
  features: PolicyFeature[];
  benefits: PolicyFeature[];
  riders: PolicyFeature[];
  limitations: PolicyFeature[];
  surrenderCharge?: string;
  withdrawalAllowance?: string;
  mvaPenalty?: string;
  rateGuarantee?: string;
};

export type PolicyData = {
  contractId: string;
  clientName: string;
  carrier: string;
  productName: string;
  issueDate: string;
  currentValue: string;
  surrenderValue: string;
  currentRate: string;
  renewalRate: string;
  guaranteedMinRate: string;
  renewalDate: string;
  isMinRateRenewal: boolean;
  suitabilityStatus: "complete" | "incomplete" | "not-started";
  eligibilityStatus: "eligible" | "restricted" | "ineligible";
  features: PolicyFeaturesData;
};

export type ProductOption = {
  ID?: string;
  productId?: string;
  id?: string;
  name: string;
  carrier: string;
  rate: string;
  term?: string;
  premiumBonus?: string | null;
  surrenderPeriod?: string;
  surrenderCharge?: string;
  freeWithdrawal?: string;
  deathBenefit?: string;
  guaranteedMinRate?: string;
  riders?: string[];
  features?: string[];
  cons?: string[];
  liquidity?: string;
  mvaPenalty?: string | null;
  licensingApproved?: boolean;
  licensingDetails?: string | null;
};

export type ComparisonData = {
  current: ProductOption;
  alternatives: ProductOption[];
  missingData: boolean;
};

export type SuitabilityScore = {
  score: number;
  reasoning: string[];
  complianceNotes: string[];
  missingData: string[];
};

export type SuitabilityData = {
  clientObjectives: string;
  riskTolerance: string;
  timeHorizon: string;
  liquidityNeeds: string;
  taxConsiderations: string;
  guaranteedIncome: string;
  rateExpectations: string;
  surrenderTimeline: string;
  livingBenefits: string[];
  advisorEligibility: string;
  score: number;
  isPrefilled: boolean;
};

export type ComparisonParameters = {
  // Profile
  residesInNursingHome: "yes" | "no";
  hasLongTermCareInsurance: "yes" | "no";
  hasMedicareSupplemental: "yes" | "no";
  // Suitability - Financial
  grossIncome: string;
  disposableIncome: string;
  taxBracket: string;
  householdLiquidAssets: string;
  monthlyLivingExpenses: string;
  totalAnnuityValue: string;
  householdNetWorth: string;
  // Anticipated Changes
  anticipateExpenseIncrease: "yes" | "no";
  anticipateIncomeDecrease: "yes" | "no";
  anticipateLiquidAssetDecrease: "yes" | "no";
  // Objectives & Planning
  financialObjectives: string;
  distributionPlan: string;
  ownedAssets: string;
  timeToFirstDistribution: string;
  expectedHoldingPeriod: string;
  sourceOfFunds: string;
  employmentStatus: string;
  applyToMeansTestedBenefits: "yes" | "no";
};

export type DisclosureItem = {
  id: string;
  label?: string;
  title?: string;
  description?: string;
  documentName?: string;
  required: boolean;
  link?: string;
};

export type TransactionOption = {
  type: "renew" | "replace";
  label: string;
  description: string;
  requirements: string[];
  warnings?: string[];
  isAvailable: boolean;
  unavailableReason?: string;
  pros?: string[];
  cons?: string[];
};

export type SubmissionStatus = {
  status: "received" | "in-review" | "nigo" | "approved" | "issued";
  timestamp: string;
  notes?: string;
};

export type SubmissionData = {
  submissionId: string;
  submittedDate: string;
  carrier: string;
  transactionType: "renew" | "replace";
  currentStatus: SubmissionStatus;
  statusHistory: SubmissionStatus[];
  nigoIssues?: {
    issue: string;
    remediation: string;
    resolved: boolean;
  }[];
};

export type AuditLogEntry = {
  timestamp: string;
  user: string;
  action: string;
  details: string;
};

export type AlertDetail = {
  alert: import("./alerts").RenewalAlert;
  clientAlerts: import("./alerts").RenewalAlert[];
  policyData: PolicyData;
  aiSuitabilityScore: SuitabilityScore;
  suitabilityData: SuitabilityData;
  disclosureItems: DisclosureItem[];
  transactionOptions: TransactionOption[];
  auditLog: AuditLogEntry[];
};

export type ClientProfile = {
  clientId: string;
  clientName: string;
  parameters: ComparisonParameters;
};

export type ComparisonResult = {
  comparisonData: ComparisonData;
};
