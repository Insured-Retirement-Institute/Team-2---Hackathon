import { logRequest, logResponse } from "./logger";
import type { SuitabilityData } from "@/types/alert-detail";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";

export async function generateAISummary(
  alertId: string,
  suitabilityData: SuitabilityData
): Promise<string> {
  if (USE_MOCKS) {
    logRequest("POST", `/api/alerts/${alertId}/ai-summary`, suitabilityData);
    await new Promise((resolve) => setTimeout(resolve, 300));
    const mockSummary = `Based on the client's ${suitabilityData.riskTolerance.toLowerCase()} risk tolerance and ${suitabilityData.timeHorizon.toLowerCase()} time horizon, this transaction aligns with their stated objectives: ${suitabilityData.clientObjectives}. The client's liquidity needs (${suitabilityData.liquidityNeeds.toLowerCase()}) and tax considerations (${suitabilityData.taxConsiderations}) support this recommendation. This product provides the guaranteed income features the client desires while maintaining appropriate surrender timeline flexibility.`;
    logResponse("POST", `/api/alerts/${alertId}/ai-summary`, { summary: mockSummary });
    return mockSummary;
  }

  const url = `${API_BASE_URL}/alerts/${alertId}/ai-summary`;
  logRequest("POST", url, suitabilityData);

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(suitabilityData),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate AI summary: ${response.statusText}`);
  }

  const data = await response.json();
  logResponse("POST", url, data);
  return data.summary;
}
