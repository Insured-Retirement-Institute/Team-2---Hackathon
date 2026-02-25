import type {
  PolicyData,
  SuitabilityScore,
  SuitabilityData,
  DisclosureItem,
  TransactionOption,
  AuditLogEntry,
  ComparisonParameters,
  ComparisonData,
  ProductOption,
} from "@/types/alert-detail";
import type { RenewalAlert } from "@/types/alerts";

/**
 * MOCK DATA - Alert detail data
 * Source: Figma project App.tsx
 */

export function getMockPolicyData(alert: RenewalAlert): PolicyData {
  return {
    contractId: alert.policyId,
    clientName: alert.clientName,
    carrier: alert.carrier,
    productName: "SecureChoice Multi-Year Guarantee Annuity",
    issueDate: "03/15/2018",
    currentValue: alert.currentValue,
    surrenderValue: `$${(parseFloat(alert.currentValue.replace(/[$,]/g, "")) * 0.98).toLocaleString()}`,
    currentRate: alert.currentRate,
    renewalRate: alert.renewalRate,
    guaranteedMinRate: "1.50%",
    renewalDate: alert.renewalDate,
    isMinRateRenewal: alert.isMinRate,
    suitabilityStatus: "incomplete",
    eligibilityStatus: "eligible",
    features: {
      surrenderCharge: "2.5% (Year 7 of 10)",
      withdrawalAllowance: "10% annually penalty-free",
      mvaPenalty: "-3.8% if surrendered today",
      rateGuarantee: "5 years remaining",
      features: [
        {
          name: "Multi-Year Rate Guarantee",
          description:
            "Fixed interest rate guaranteed for the full term with no market volatility risk.",
          included: true,
          type: "feature",
        },
        {
          name: "Principal Protection",
          description: "100% principal protection from market downturns.",
          included: true,
          type: "feature",
        },
        {
          name: "Guaranteed Growth",
          description:
            "Interest compounds daily and is credited annually. Minimum guaranteed rate of 1.50%.",
          included: true,
          type: "feature",
        },
        {
          name: "1035 Exchange Eligible",
          description:
            "Can be exchanged tax-free for another qualified annuity under IRC Section 1035.",
          included: true,
          type: "feature",
        },
      ],
      benefits: [
        {
          name: "Tax-Deferred Growth",
          description: "Interest earnings grow tax-deferred until withdrawal.",
          included: true,
          type: "benefit",
        },
        {
          name: "Death Benefit",
          description:
            "Beneficiaries receive full account value without reduction.",
          included: true,
          type: "benefit",
        },
        {
          name: "Annual Free Withdrawal",
          description:
            "10% of account value can be withdrawn each year without penalty.",
          included: true,
          type: "benefit",
        },
        {
          name: "Nursing Home Waiver",
          description:
            "Full surrender charge waiver if confined to nursing facility for 90+ consecutive days.",
          included: true,
          type: "benefit",
        },
      ],
      riders: [
        {
          name: "Enhanced Death Benefit Rider",
          description:
            "Provides an additional 10% bonus to death benefit proceeds.",
          included: false,
          type: "rider",
        },
        {
          name: "Income Guarantee Rider",
          description:
            "Guarantees minimum income percentage regardless of account value.",
          included: false,
          type: "rider",
        },
        {
          name: "Long-Term Care Acceleration",
          description:
            "Allows accelerated access to death benefit if qualified for long-term care.",
          included: false,
          type: "rider",
        },
      ],
      limitations: [
        {
          name: "Surrender Charge Period",
          description:
            "7 of 10-year surrender period remaining. Early withdrawal beyond free amount subject to 2.5% penalty.",
          included: true,
          type: "limitation",
        },
        {
          name: "Market Value Adjustment (MVA)",
          description:
            "Surrenders during guarantee period subject to MVA. Current penalty is -3.8%.",
          included: true,
          type: "limitation",
        },
        {
          name: "Liquidity Restrictions",
          description:
            "Limited access to funds beyond 10% annual free withdrawal.",
          included: true,
          type: "limitation",
        },
        {
          name: "Rate Renewal Risk",
          description:
            "At end of guarantee period, renewal rate may be significantly lower.",
          included: true,
          type: "limitation",
        },
        {
          name: "No Market Upside Participation",
          description:
            "Fixed rate means no ability to benefit from rising interest rates or equity market gains.",
          included: true,
          type: "limitation",
        },
      ],
    },
  };
}

export const mockSuitabilityScore: SuitabilityScore = {
  score: 85,
  reasoning: [
    "Client's conservative risk tolerance aligns with fixed annuity structure and guaranteed returns",
    "Long-term time horizon (7+ years) matches optimal surrender period for alternative products",
    "Current minimum rate renewal significantly underperforms market alternatives by 2.7-2.9%",
    "Client's liquidity needs are met with 10% annual free withdrawal provisions",
  ],
  complianceNotes: [
    "1035 exchange documentation required for replacement transaction",
    "State-specific replacement forms must be completed and filed",
    "Client acknowledgment of new surrender period required",
    "Carrier appointment verification completed successfully",
  ],
  missingData: [],
};

export const mockSuitabilityData: SuitabilityData = {
  clientObjectives:
    "Principal protection with moderate growth, estate planning for beneficiaries",
  riskTolerance: "conservative",
  timeHorizon: "long",
  liquidityNeeds: "Minimal: Rarely need access",
  taxConsiderations:
    "Tax efficiency: High priority - Critical priority. Deferred Income: Distributions in 5+ years",
  guaranteedIncome: "preferred",
  rateExpectations:
    "Rate expectations: Above Average - Better than market rates",
  surrenderTimeline: "9-10",
  livingBenefits: ["death-benefit"],
  advisorEligibility: "all-carriers",
  score: 100,
  isPrefilled: true,
};

export const mockDisclosureItems: DisclosureItem[] = [
  {
    id: "d1",
    title: "Product Disclosure Review",
    description: "I have reviewed all product disclosures with the client",
    documentName: "Form ADV Part 2A - Client Brochure",
    required: true,
  },
  {
    id: "d2",
    title: "Surrender Period & Withdrawals",
    description:
      "Client understands the surrender period and withdrawal restrictions",
    documentName: "Annuity Surrender Schedule Disclosure",
    required: true,
  },
  {
    id: "d3",
    title: "Replacement Transaction Notice",
    description:
      "Client acknowledges this is a replacement transaction subject to regulatory review",
    documentName: "NAIC Form 1035 Exchange Notice",
    required: true,
  },
  {
    id: "d4",
    title: "Suitability Documentation",
    description:
      "I have documented the complete suitability rationale in the client file",
    documentName: "Client Suitability Worksheet (Internal)",
    required: true,
  },
  {
    id: "d5",
    title: "Comparison Disclosure Form",
    description:
      "Client has been provided with and reviewed the required comparison disclosure form",
    documentName: "Product Comparison & Cost Disclosure",
    required: true,
  },
];

export function getMockTransactionOptions(
  alert: RenewalAlert,
  comparisonData: ComparisonData,
): TransactionOption[] {
  const options: TransactionOption[] = [
    {
      type: "renew",
      label: `Continue with ${alert.carrier} at renewal rate of ${alert.renewalRate}`,
      description: "",
      requirements: [],
      warnings: [],
      pros: [
        "No new paperwork or underwriting",
        "Maintains existing carrier relationship",
        "Surrender period already expired or minimal remaining",
      ],
      cons: [
        `Significant rate drop to guaranteed minimum ${alert.renewalRate}`,
        `Missing opportunity to capture higher market rates (${comparisonData.alternatives[0]?.rate || "4.2%"} available)`,
        "Lower returns for client over policy term",
      ],
      isAvailable: true,
    },
  ];

  comparisonData.alternatives.forEach((alt) => {
    const pros: string[] = [];
    const currentRate = parseFloat(alert.renewalRate);
    const newRate = parseFloat(alt.rate.replace("%", ""));
    pros.push(
      `Rate improvement: ${(newRate - currentRate).toFixed(1)}% increase (${alert.renewalRate} → ${alt.rate})`,
    );
    if (alt.premiumBonus)
      pros.push(`${alt.premiumBonus} premium bonus on entire account value`);
    pros.push(
      "Enhanced features including death benefit protection",
      `Strong carrier rating (${alt.carrier})`,
    );

    options.push({
      type: "replace",
      label: `1035 exchange to ${alt.carrier} ${alt.name} at ${alt.rate}${alt.premiumBonus ? ` with ${alt.premiumBonus} premium bonus` : ""}`,
      description: "",
      requirements: [
        alt.licensingApproved
          ? `Licensed with ${alt.carrier} - Verified ✓`
          : `Licensing required with ${alt.carrier}`,
        "1035 exchange documentation",
        "State replacement forms",
        `New surrender period applies (${alt.surrenderPeriod} years)`,
      ],
      warnings: [
        `New surrender charges apply for ${alt.surrenderPeriod} years`,
      ],
      pros,
      cons: [
        `New ${alt.surrenderPeriod}-year surrender period begins`,
        "Requires 1035 exchange paperwork",
        "State replacement forms and review period",
        "Client must acknowledge new terms and conditions",
      ],
      isAvailable: alt.licensingApproved ?? false,
    });
  });

  return options;
}

export const mockAuditLog: AuditLogEntry[] = [
  {
    timestamp: new Date().toLocaleString(),
    user: "advisor@firm.com",
    action: "Alert viewed",
    details: "Policy opened for review",
  },
  {
    timestamp: new Date(Date.now() - 120000).toLocaleString(),
    user: "advisor@firm.com",
    action: "Comparison generated",
    details: "Current vs 3 alternatives",
  },
  {
    timestamp: new Date(Date.now() - 240000).toLocaleString(),
    user: "advisor@firm.com",
    action: "Suitability analysis run",
    details: "Score: 85/100",
  },
  {
    timestamp: new Date(Date.now() - 360000).toLocaleString(),
    user: "advisor@firm.com",
    action: "Suitability data updated",
    details: "Client objectives modified",
  },
];

export const mockComparisonParameters: ComparisonParameters = {
  residesInNursingHome: "no",
  hasLongTermCareInsurance: "no",
  hasMedicareSupplemental: "yes",
  grossIncome: "85000",
  disposableIncome: "45000",
  taxBracket: "22%",
  householdLiquidAssets: "250000",
  monthlyLivingExpenses: "4500",
  totalAnnuityValue: "180000",
  householdNetWorth: "650000",
  anticipateExpenseIncrease: "no",
  anticipateIncomeDecrease: "no",
  anticipateLiquidAssetDecrease: "no",
  financialObjectives: "accumulation",
  distributionPlan: "beneficiaries",
  ownedAssets: "annuities",
  timeToFirstDistribution: "10-plus",
  expectedHoldingPeriod: "10-plus",
  sourceOfFunds: "annuity",
  employmentStatus: "retired",
  applyToMeansTestedBenefits: "no",
};

export function getMockComparisonData(alert: RenewalAlert): ComparisonData {
  return {
    current: {
      id: "prod-securechoice",
      name: "SecureChoice MYGA",
      carrier: alert.carrier,
      rate: alert.currentRate,
      term: "5 years (renewing at 1 year)",
      guaranteedMinRate: "1.50%",
      surrenderPeriod: "7",
      surrenderCharge: "2.5%",
      freeWithdrawal: "10%",
      deathBenefit: "Account Value",
      mvaPenalty: "-3.8%",
      licensingApproved: true,
      riders: [
        "Tax-Deferred Growth",
        "Free Annual Withdrawal (10%)",
        "Nursing Home Waiver",
      ],
    },
    alternatives: [
      {
        id: "prod-flexgrowth",
        name: "FlexGrowth Plus MYGA",
        carrier: "Great American",
        rate: "4.25%",
        term: "7 years",
        premiumBonus: "3.0%",
        guaranteedMinRate: "2.50%",
        surrenderPeriod: "7",
        surrenderCharge: "7% (declining)",
        freeWithdrawal: "10%",
        deathBenefit: "Enhanced",
        mvaPenalty: "None",
        licensingApproved: true,
        licensingDetails:
          "Active carrier appointment confirmed. Licensed in 47 states.",
        riders: [
          "3% Premium Bonus",
          "Enhanced Death Benefit (+10%)",
          "Tax-Deferred Growth",
          "Free Annual Withdrawal (10%)",
          "Nursing Home Waiver",
        ],
      },
      {
        id: "prod-secureincome",
        name: "Secure Income Pro MYGA",
        carrier: "North American",
        rate: "3.95%",
        term: "5 years",
        guaranteedMinRate: "2.00%",
        surrenderPeriod: "5",
        surrenderCharge: "5% (declining)",
        freeWithdrawal: "15%",
        deathBenefit: "Account Value",
        mvaPenalty: "-2.1%",
        licensingApproved: false,
        licensingDetails:
          "Carrier appointment pending. Product training required.",
        riders: [
          "Tax-Deferred Growth",
          "Enhanced Free Withdrawal (15%)",
          "Nursing Home Waiver",
          "Terminal Illness Waiver",
        ],
      },
      {
        id: "prod-premiumshield",
        name: "Premium Shield MYGA",
        carrier: "American Equity",
        rate: "4.10%",
        term: "6 years",
        premiumBonus: "2.0%",
        guaranteedMinRate: "1.75%",
        surrenderPeriod: "6",
        surrenderCharge: "6% (declining)",
        freeWithdrawal: "10%",
        deathBenefit: "Enhanced",
        mvaPenalty: "-2.5%",
        licensingApproved: true,
        licensingDetails:
          "Fully approved. Active carrier appointment current through 12/31/2026.",
        riders: [
          "2% Premium Bonus",
          "Tax-Deferred Growth",
          "Free Annual Withdrawal (10%)",
        ],
      },
    ],
    missingData: false,
  };
}

export function getMockProductShelf(): ProductOption[] {
  return [
    {
      id: "prod-flexgrowth",
      name: "FlexGrowth Plus MYGA",
      carrier: "Great American",
      rate: "4.25%",
      term: "7 years",
      premiumBonus: "3.0%",
      guaranteedMinRate: "2.50%",
      surrenderPeriod: "7",
      surrenderCharge: "7% (declining)",
      freeWithdrawal: "10%",
      deathBenefit: "Enhanced",
      mvaPenalty: "None",
      licensingApproved: true,
      licensingDetails: "Active carrier appointment confirmed.",
      riders: [
        "3% Premium Bonus",
        "Enhanced Death Benefit (+10%)",
        "Nursing Home Waiver",
      ],
    },
    {
      id: "prod-secureincome",
      name: "Secure Income Pro MYGA",
      carrier: "North American",
      rate: "3.95%",
      term: "5 years",
      guaranteedMinRate: "2.00%",
      surrenderPeriod: "5",
      surrenderCharge: "5% (declining)",
      freeWithdrawal: "15%",
      deathBenefit: "Account Value",
      mvaPenalty: "-2.1%",
      licensingApproved: false,
      licensingDetails:
        "Carrier appointment pending. Product training required.",
      riders: [
        "Enhanced Free Withdrawal (15%)",
        "Nursing Home Waiver",
        "Terminal Illness Waiver",
      ],
    },
    {
      id: "prod-premiumshield",
      name: "Premium Shield MYGA",
      carrier: "American Equity",
      rate: "4.10%",
      term: "6 years",
      premiumBonus: "2.0%",
      guaranteedMinRate: "1.75%",
      surrenderPeriod: "6",
      surrenderCharge: "6% (declining)",
      freeWithdrawal: "10%",
      deathBenefit: "Enhanced",
      mvaPenalty: "-2.5%",
      licensingApproved: true,
      licensingDetails: "Fully approved through 12/31/2026.",
      riders: ["2% Premium Bonus", "Nursing Home Waiver"],
    },
    {
      id: "prod-safeharbor",
      name: "SafeHarbor Fixed Annuity",
      carrier: "Athene",
      rate: "4.40%",
      term: "5 years",
      guaranteedMinRate: "2.25%",
      surrenderPeriod: "5",
      surrenderCharge: "5% (declining)",
      freeWithdrawal: "10%",
      deathBenefit: "Account Value",
      mvaPenalty: "None",
      licensingApproved: true,
      riders: ["Tax-Deferred Growth", "Nursing Home Waiver"],
    },
    {
      id: "prod-pinnacle",
      name: "Pinnacle Rate MYGA",
      carrier: "Global Atlantic",
      rate: "4.50%",
      term: "7 years",
      premiumBonus: "1.5%",
      guaranteedMinRate: "2.00%",
      surrenderPeriod: "7",
      surrenderCharge: "8% (declining)",
      freeWithdrawal: "10%",
      deathBenefit: "Enhanced",
      mvaPenalty: "-3.0%",
      licensingApproved: true,
      riders: [
        "1.5% Premium Bonus",
        "Enhanced Death Benefit",
        "Nursing Home Waiver",
        "Terminal Illness Waiver",
      ],
    },
    {
      id: "prod-valuelock",
      name: "ValueLock 3-Year MYGA",
      carrier: "Midland National",
      rate: "3.75%",
      term: "3 years",
      guaranteedMinRate: "1.50%",
      surrenderPeriod: "3",
      surrenderCharge: "3% (declining)",
      freeWithdrawal: "10%",
      deathBenefit: "Account Value",
      mvaPenalty: "None",
      licensingApproved: true,
      riders: ["Tax-Deferred Growth", "Nursing Home Waiver"],
    },
    {
      id: "prod-horizon",
      name: "Horizon Growth MYGA",
      carrier: "Jackson National",
      rate: "4.15%",
      term: "5 years",
      premiumBonus: "2.5%",
      guaranteedMinRate: "1.75%",
      surrenderPeriod: "5",
      surrenderCharge: "6% (declining)",
      freeWithdrawal: "10%",
      deathBenefit: "Enhanced",
      mvaPenalty: "-1.8%",
      licensingApproved: false,
      licensingDetails: "Product training required before selling.",
      riders: [
        "2.5% Premium Bonus",
        "Enhanced Death Benefit (+5%)",
        "Nursing Home Waiver",
      ],
    },
    {
      id: "prod-legacy",
      name: "Legacy Plus 10 MYGA",
      carrier: "Nationwide",
      rate: "4.65%",
      term: "10 years",
      premiumBonus: "4.0%",
      guaranteedMinRate: "2.75%",
      surrenderPeriod: "10",
      surrenderCharge: "10% (declining)",
      freeWithdrawal: "10%",
      deathBenefit: "Enhanced",
      mvaPenalty: "-4.0%",
      licensingApproved: true,
      riders: [
        "4% Premium Bonus",
        "Enhanced Death Benefit (+15%)",
        "Nursing Home Waiver",
        "Terminal Illness Waiver",
        "RMD-Friendly Withdrawals",
      ],
    },
    {
      id: "prod-quickaccess",
      name: "QuickAccess MYGA",
      carrier: "Fidelity & Guaranty",
      rate: "3.60%",
      term: "3 years",
      guaranteedMinRate: "1.25%",
      surrenderPeriod: "3",
      surrenderCharge: "3% (declining)",
      freeWithdrawal: "20%",
      deathBenefit: "Account Value",
      mvaPenalty: "None",
      licensingApproved: true,
      riders: ["Enhanced Free Withdrawal (20%)", "Nursing Home Waiver"],
    },
  ];
}
