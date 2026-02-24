import type { RenewalAlert } from "@/types/alerts";

/**
 * MOCK DATA - This will be replaced with real API calls
 * Source: Figma project generateMockAlerts()
 */
export const mockAlerts: RenewalAlert[] = [
  // Maria Rodriguez - 2 alerts (replacement + suitability)
  {
    id: "alert-ANN-2020-5621-renewal",
    policyId: "ANN-2020-5621",
    clientName: "Maria Rodriguez",
    carrier: "Athene",
    renewalDate: "15 Days",
    daysUntilRenewal: 15,
    currentRate: "3.8%",
    renewalRate: "1.5%",
    currentValue: "$180,000",
    isMinRate: true,
    priority: "high",
    hasDataException: false,
    status: "pending",
    alertType: "replacement_recommended",
    alertTypes: ["replacement_recommended", "suitability_review", "missing_info"],
    alertDescription: "Renewal at minimum rate - replacement analysis recommended"
  },
  {
    id: "alert-ANN-2020-5621-suitability",
    policyId: "ANN-2020-5621",
    clientName: "Maria Rodriguez",
    carrier: "Athene",
    renewalDate: "N/A",
    daysUntilRenewal: 15,
    currentRate: "3.8%",
    renewalRate: "3.2%",
    currentValue: "$180,000",
    isMinRate: false,
    priority: "medium",
    hasDataException: false,
    status: "pending",
    alertType: "suitability_review",
    alertDescription: "Annual suitability review required - client objectives may have changed"
  },

  // Robert Chen - 1 alert (replacement)
  {
    id: "alert-ANN-2019-8934",
    policyId: "ANN-2019-8934",
    clientName: "Robert Chen",
    carrier: "Nationwide",
    renewalDate: "28 Days",
    daysUntilRenewal: 28,
    currentRate: "4.1%",
    renewalRate: "1.5%",
    currentValue: "$315,000",
    isMinRate: true,
    priority: "high",
    hasDataException: false,
    status: "pending",
    alertType: "replacement_recommended",
    alertDescription: "Renewal at minimum rate - replacement analysis recommended"
  },

  // David Thompson - 1 alert (replacement)
  {
    id: "alert-ANN-2020-7123-renewal",
    policyId: "ANN-2020-7123",
    clientName: "David Thompson",
    carrier: "Allianz",
    renewalDate: "18 Days",
    daysUntilRenewal: 18,
    currentRate: "3.5%",
    renewalRate: "1.5%",
    currentValue: "$156,000",
    isMinRate: true,
    priority: "high",
    hasDataException: false,
    status: "pending",
    alertType: "replacement_recommended",
    alertDescription: "Renewal at minimum rate - replacement analysis recommended"
  },

  // Jessica Martinez - 1 alert (suitability)
  {
    id: "alert-ANN-2019-3421",
    policyId: "ANN-2019-3421",
    clientName: "Jessica Martinez",
    carrier: "Nationwide",
    renewalDate: "65 Days",
    daysUntilRenewal: 65,
    currentRate: "3.2%",
    renewalRate: "2.5%",
    currentValue: "$135,000",
    isMinRate: false,
    priority: "medium",
    hasDataException: false,
    status: "pending",
    alertType: "suitability_review",
    alertDescription: "Annual suitability review required - moderate rate drop at renewal"
  },

  // Daniel Garcia - 2 alerts (replacement + missing info)
  {
    id: "alert-ANN-2020-7845-renewal",
    policyId: "ANN-2020-7845",
    clientName: "Daniel Garcia",
    carrier: "Pacific Life",
    renewalDate: "74 Days",
    daysUntilRenewal: 74,
    currentRate: "3.9%",
    renewalRate: "2.9%",
    currentValue: "$178,000",
    isMinRate: false,
    priority: "low",
    hasDataException: false,
    status: "pending",
    alertType: "replacement_recommended",
    alertDescription: "Standard renewal - rate remains competitive"
  },
  {
    id: "alert-ANN-2020-7845-missing",
    policyId: "ANN-2020-7845",
    clientName: "Daniel Garcia",
    carrier: "Pacific Life",
    renewalDate: "N/A",
    daysUntilRenewal: 74,
    currentRate: "3.9%",
    renewalRate: "2.9%",
    currentValue: "$178,000",
    isMinRate: false,
    priority: "low",
    hasDataException: true,
    missingFields: ["Contact phone update needed"],
    status: "pending",
    alertType: "missing_info",
    alertDescription: "Client contact information needs update"
  },

  // Nancy White - 1 alert (suitability)
  {
    id: "alert-ANN-2019-2134",
    policyId: "ANN-2019-2134",
    clientName: "Nancy White",
    carrier: "Allianz",
    renewalDate: "82 Days",
    daysUntilRenewal: 82,
    currentRate: "3.5%",
    renewalRate: "2.7%",
    currentValue: "$145,000",
    isMinRate: false,
    priority: "medium",
    hasDataException: false,
    status: "pending",
    alertType: "suitability_review",
    alertDescription: "Annual suitability review required - client objectives confirmation needed"
  },

  // George Robinson - 1 alert (replacement)
  {
    id: "alert-ANN-2021-5678",
    policyId: "ANN-2021-5678",
    clientName: "George Robinson",
    carrier: "Allianz",
    renewalDate: "98 Days",
    daysUntilRenewal: 98,
    currentRate: "3.3%",
    renewalRate: "2.8%",
    currentValue: "$145,000",
    isMinRate: false,
    priority: "low",
    hasDataException: false,
    status: "pending",
    alertType: "replacement_recommended",
    alertDescription: "Replacement analysis recommended - review available alternatives"
  },

  // Jennifer Martinez - 1 alert (income planning)
  {
    id: "alert-ANN-2018-3456-income",
    policyId: "ANN-2018-3456",
    clientName: "Jennifer Martinez",
    carrier: "Pacific Life",
    renewalDate: "N/A",
    daysUntilRenewal: 45,
    currentRate: "4.0%",
    renewalRate: "3.5%",
    currentValue: "$225,000",
    isMinRate: false,
    priority: "medium",
    hasDataException: false,
    status: "pending",
    alertType: "income_planning",
    alertDescription: "Client approaching income distribution phase - income planning review recommended"
  }
];
