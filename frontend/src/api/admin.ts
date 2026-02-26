import { logRequest, logResponse } from "./logger";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";

export interface SystemHealthMetric {
  time: string;
  requests: number;
  successRate: number;
  avgResponseTime: number;
  errors: number;
}

export interface BiasMetric {
  category: string;
  actual: number;
  expected: number;
  variance: number;
  status: "healthy" | "warning" | "alert";
}

export interface ComplianceMetric {
  area: string;
  score: number;
  total: number;
  compliant: number;
  flagged: number;
  trend: "up" | "down" | "stable";
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  agent: string;
  action: string;
  clientId: string;
  result: "Success" | "Warning" | "Flagged";
  biasScore: number;
  complianceScore: number;
}

export interface AgentStatus {
  name: string;
  status: "healthy" | "warning" | "error";
  uptime: number;
  requests: number;
  avgLatency: number;
}

export interface APIEndpoint {
  name: string;
  status: "healthy" | "warning" | "error";
  uptime: number;
  calls: number;
  errors: number;
}

export interface AdminDashboardData {
  systemHealth: SystemHealthMetric[];
  biasMetrics: BiasMetric[];
  complianceMetrics: ComplianceMetric[];
  auditLog: AuditLogEntry[];
  agentStatus: AgentStatus[];
  apiEndpoints: APIEndpoint[];
  overallBiasScore: number;
  overallComplianceScore: number;
  totalRequests: number;
  avgSuccessRate: number;
  totalErrors: number;
}

export async function fetchAdminDashboard(): Promise<AdminDashboardData> {
  if (USE_MOCKS) {
    logRequest("GET", "/api/admin/dashboard");
    await new Promise((resolve) => setTimeout(resolve, 500));
    const mockData: AdminDashboardData = {
      systemHealth: [],
      biasMetrics: [],
      complianceMetrics: [],
      auditLog: [],
      agentStatus: [],
      apiEndpoints: [],
      overallBiasScore: 89,
      overallComplianceScore: 99,
      totalRequests: 4234,
      avgSuccessRate: 98.6,
      totalErrors: 12,
    };
    logResponse("GET", "/api/admin/dashboard (mock)", mockData);
    return mockData;
  }

  const url = `${API_BASE_URL}/admin/dashboard`;
  logRequest("GET", url);

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch admin dashboard: ${response.statusText}`);
  }

  const data = await response.json();
  logResponse("GET", url, data);
  return data;
}
