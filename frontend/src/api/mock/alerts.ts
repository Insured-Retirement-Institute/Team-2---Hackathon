import type { RenewalAlert } from "@/types/alerts";
import policyDataFile from "../../../.iri/context/policyData.json";

/**
 * REAL DATA - Generated from context files
 */

// Helper to calculate days until renewal
function getDaysUntilRenewal(renewalDate: string): number {
  const parts = renewalDate.split("/");
  const renewal = new Date(
    parseInt(parts[2]),
    parseInt(parts[0]) - 1,
    parseInt(parts[1])
  );
  const today = new Date();
  const diff = renewal.getTime() - today.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

// Generate alerts from real policy data
function generateAlertsFromPolicyData(): RenewalAlert[] {
  const alerts: RenewalAlert[] = [];

  policyDataFile.policyData.forEach((policy) => {
    const daysUntil = getDaysUntilRenewal(policy.renewalDate);

    // Only include policies renewing within 90 days and eligible
    if (daysUntil > 0 && daysUntil <= 90 && policy.eligibilityStatus === "eligible") {
      const alertTypes: Array<
        | "replacement_recommended"
        | "suitability_review"
        | "missing_info"
      > = [];

      if (policy.isMinRateRenewal) {
        alertTypes.push("replacement_recommended");
      }

      if (policy.suitabilityStatus === "incomplete" || policy.suitabilityStatus === "not-started") {
        alertTypes.push("suitability_review");
      }

      const priority =
        policy.isMinRateRenewal || daysUntil <= 30
          ? "high"
          : daysUntil <= 60
            ? "medium"
            : "low";

      alerts.push({
        id: `alert-${policy.contractId}`,
        clientId: policy.clientId,
        policyId: policy.contractId,
        clientName: policy.clientName,
        carrier: policy.carrier,
        renewalDate: `${daysUntil} Days`,
        daysUntilRenewal: daysUntil,
        currentRate: policy.currentRate,
        renewalRate: policy.renewalRate,
        currentValue: policy.currentValue,
        isMinRate: policy.isMinRateRenewal,
        priority,
        hasDataException: false,
        status: "pending",
        alertType: alertTypes[0] || "replacement_recommended",
        alertTypes,
        alertDescription: policy.isMinRateRenewal
          ? "Renewal at minimum rate - replacement analysis recommended"
          : `Rate changing from ${policy.currentRate} to ${policy.renewalRate}`,
      });
    }
  });

  // Sort by days until renewal (most urgent first)
  return alerts.sort((a, b) => a.daysUntilRenewal - b.daysUntilRenewal);
}

export const mockAlerts: RenewalAlert[] = generateAlertsFromPolicyData();
