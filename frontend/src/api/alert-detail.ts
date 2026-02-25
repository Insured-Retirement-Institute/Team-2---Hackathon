import type {
  AlertDetail,
  ClientProfile,
  ComparisonParameters,
  ComparisonResult,
  ProductOption,
  SuitabilityData,
  SubmissionData,
} from "@/types/alert-detail";
import { mockAlerts } from "./mock/alerts";
import { logRequest, logResponse } from "./logger";
import {
  getMockPolicyData,
  mockSuitabilityScore,
  mockSuitabilityData,
  mockDisclosureItems,
  getMockTransactionOptions,
  mockAuditLog,
  mockComparisonParameters,
  getMockComparisonData,
} from "./mock/alert-detail";

/**
 * API Service Layer - Alert Detail
 * Currently returns mock data - ready to be replaced with real API calls
 * When switching to real APIs, use: const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
 */

/**
 * Fetch alert detail with policy data
 * GET /api/alerts/{alertId}
 */
export async function fetchAlertDetail(alertId: string): Promise<AlertDetail> {
  logRequest("GET /api/alerts/{alertId}", { alertId });
  return new Promise((resolve) => {
    setTimeout(() => {
      const alert = mockAlerts.find((a) => a.id === alertId) ?? mockAlerts[0];
      const clientAlerts = mockAlerts.filter((a) => a.clientName === alert.clientName);
      const comparisonData = getMockComparisonData(alert);
      const r = { alert, clientAlerts, policyData: getMockPolicyData(alert), aiSuitabilityScore: mockSuitabilityScore, suitabilityData: mockSuitabilityData, disclosureItems: mockDisclosureItems, transactionOptions: getMockTransactionOptions(alert, comparisonData), auditLog: mockAuditLog };
      logResponse("GET /api/alerts/{alertId}", r);
      resolve(r);
    }, 300);
  });
}

/**
 * Fetch client profile (comparison parameters)
 * GET /api/clients/{clientId}/profile
 */
export async function fetchClientProfile(_clientId: string): Promise<ClientProfile> {
  logRequest("GET /api/clients/{clientId}/profile", { clientId: _clientId });
  return new Promise((resolve) => {
    setTimeout(() => {
      const r = { clientId: _clientId, clientName: "Maria Rodriguez", parameters: mockComparisonParameters };
      logResponse("GET /api/clients/{clientId}/profile", r);
      resolve(r);
    }, 300);
  });
}

/**
 * Save client profile (comparison parameters)
 * PUT /api/clients/{clientId}/profile
 */
export async function saveClientProfile(_clientId: string, _parameters: ComparisonParameters): Promise<void> {
  logRequest("PUT /api/clients/{clientId}/profile", { clientId: _clientId, parameters: _parameters });
  return new Promise((resolve) => {
    setTimeout(() => { logResponse("PUT /api/clients/{clientId}/profile", { success: true }); resolve(); }, 300);
  });
}

/**
 * Run comparison analysis
 * POST /api/alerts/{alertId}/compare
 */
export async function runComparison(alertId: string): Promise<ComparisonResult> {
  logRequest("POST /api/alerts/{alertId}/compare", { alertId });
  return new Promise((resolve) => {
    setTimeout(() => {
      const alert = mockAlerts.find((a) => a.id === alertId) ?? mockAlerts[0];
      const r = { comparisonData: getMockComparisonData(alert) };
      logResponse("POST /api/alerts/{alertId}/compare", r);
      resolve(r);
    }, 500);
  });
}

/**
 * Re-run comparison with specific products selected from shelf
 * POST /api/alerts/{alertId}/compare/products
 */
export async function recompareWithProducts(alertId: string, selectedProducts: ProductOption[]): Promise<ComparisonResult> {
  logRequest("POST /api/alerts/{alertId}/compare/products", { alertId, selectedProducts });
  return new Promise((resolve) => {
    setTimeout(() => {
      const alert = mockAlerts.find((a) => a.id === alertId) ?? mockAlerts[0];
      const base = getMockComparisonData(alert);
      const r = { comparisonData: { ...base, alternatives: selectedProducts } };
      logResponse("POST /api/alerts/{alertId}/compare/products", r);
      resolve(r);
    }, 400);
  });
}

/**
 * Save suitability data
 * PUT /api/alerts/{alertId}/suitability
 */
export async function saveSuitability(_alertId: string, _data: SuitabilityData): Promise<void> {
  logRequest("PUT /api/alerts/{alertId}/suitability", { alertId: _alertId, data: _data });
  return new Promise((resolve) => {
    setTimeout(() => { logResponse("PUT /api/alerts/{alertId}/suitability", { success: true }); resolve(); }, 300);
  });
}

/**
 * Save disclosure acknowledgments
 * PUT /api/alerts/{alertId}/disclosures
 */
export async function saveDisclosures(_alertId: string, _acknowledgedIds: string[]): Promise<void> {
  logRequest("PUT /api/alerts/{alertId}/disclosures", { alertId: _alertId, acknowledgedIds: _acknowledgedIds });
  return new Promise((resolve) => {
    setTimeout(() => { logResponse("PUT /api/alerts/{alertId}/disclosures", { success: true }); resolve(); }, 300);
  });
}

/**
 * Submit transaction
 * POST /api/alerts/{alertId}/transaction
 */
export async function submitTransaction(
  _alertId: string,
  _data: { type: "renew" | "replace"; rationale: string; clientStatement: string }
): Promise<SubmissionData> {
  logRequest("POST /api/alerts/{alertId}/transaction", { alertId: _alertId, data: _data });
  return new Promise((resolve) => {
    setTimeout(() => {
      const submissionId = `SUB-2026-${Math.floor(Math.random() * 10000)}`;
      const r: SubmissionData = {
        submissionId,
        submittedDate: new Date().toLocaleDateString(),
        carrier: "Great American",
        transactionType: _data.type,
        currentStatus: { status: "received", timestamp: new Date().toLocaleString(), notes: "Application received and queued for carrier review" },
        statusHistory: [{ status: "received", timestamp: new Date().toLocaleString(), notes: "Application received and queued for carrier review" }],
      };
      logResponse("POST /api/alerts/{alertId}/transaction", r);
      resolve(r);
    }, 500);
  });
}
