import type { RenewalAlert, DashboardStats } from "@/types/alerts";
import { logRequest, logResponse } from "./logger";
import { mockAlerts } from "./mock/alerts";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";

/**
 * Fetch all renewal alerts
 * GET /api/alerts
 */
export async function fetchAlerts(): Promise<RenewalAlert[]> {
  logRequest("GET /api/alerts");
  
  if (USE_MOCKS) {
    return new Promise((resolve) => {
      setTimeout(() => {
        logResponse("GET /api/alerts (mock)", mockAlerts);
        resolve(mockAlerts);
      }, 300);
    });
  }

  const res = await fetch(`${API_BASE_URL}/alerts`);
  if (!res.ok) throw new Error(`Failed to fetch alerts: ${res.statusText}`);
  const r = await res.json();
  logResponse("GET /api/alerts", r);
  return r;
}

/**
 * Fetch dashboard statistics
 * GET /api/dashboard/stats
 */
export async function fetchDashboardStats(): Promise<DashboardStats> {
  logRequest("GET /api/dashboard/stats");
  
  if (USE_MOCKS) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const stats: DashboardStats = {
          total: mockAlerts.length,
          high: mockAlerts.filter((a) => a.priority === "high").length,
          urgent: mockAlerts.filter((a) => a.daysUntilRenewal <= 30).length,
          totalValue: mockAlerts.reduce((sum, a) => {
            const value = parseFloat(a.currentValue.replace(/[$,]/g, ""));
            return sum + value;
          }, 0),
        };
        logResponse("GET /api/dashboard/stats (mock)", stats);
        resolve(stats);
      }, 300);
    });
  }

  const res = await fetch(`${API_BASE_URL}/dashboard/stats`);
  if (!res.ok)
    throw new Error(`Failed to fetch dashboard stats: ${res.statusText}`);
  const r = await res.json();
  logResponse("GET /api/dashboard/stats", r);
  return r;
}

/**
 * Snooze an alert
 * POST /api/alerts/{alertId}/snooze
 */
export async function snoozeAlert(
  alertId: string,
  snoozeDays: number,
): Promise<void> {
  logRequest("POST /api/alerts/{alertId}/snooze", { alertId, snoozeDays });
  
  if (USE_MOCKS) {
    return new Promise((resolve) => {
      setTimeout(() => {
        logResponse("POST /api/alerts/{alertId}/snooze (mock)", { success: true });
        resolve();
      }, 300);
    });
  }

  const res = await fetch(`${API_BASE_URL}/alerts/${alertId}/snooze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ snoozeDays }),
  });
  if (!res.ok) throw new Error(`Failed to snooze alert: ${res.statusText}`);
  const r = await res.json();
  logResponse("POST /api/alerts/{alertId}/snooze", r);
}

/**
 * Dismiss an alert
 * POST /api/alerts/{alertId}/dismiss
 */
export async function dismissAlert(
  alertId: string,
  reason: string,
): Promise<void> {
  logRequest("POST /api/alerts/{alertId}/dismiss", { alertId, reason });
  
  if (USE_MOCKS) {
    return new Promise((resolve) => {
      setTimeout(() => {
        logResponse("POST /api/alerts/{alertId}/dismiss (mock)", { success: true });
        resolve();
      }, 300);
    });
  }

  const res = await fetch(`${API_BASE_URL}/alerts/${alertId}/dismiss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error(`Failed to dismiss alert: ${res.statusText}`);
  const r = await res.json();
  logResponse("POST /api/alerts/{alertId}/dismiss", r);
}
