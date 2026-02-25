import type { RenewalAlert, DashboardStats } from "@/types/alerts";
import { mockAlerts } from "./mock/alerts";
import { logRequest, logResponse } from "./logger";

/**
 * API Service Layer
 * Currently returns mock data - ready to be replaced with real API calls
 * When switching to real APIs, use: const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";
 */

/**
 * Fetch all renewal alerts
 * GET /api/alerts
 */
export async function fetchAlerts(): Promise<RenewalAlert[]> {
  logRequest("GET /api/alerts");
  return new Promise((resolve) => {
    setTimeout(() => { const r = mockAlerts; logResponse("GET /api/alerts", r); resolve(r); }, 300);
  });
}

/**
 * Fetch dashboard statistics
 * GET /api/dashboard/stats
 */
export async function fetchDashboardStats(): Promise<DashboardStats> {
  logRequest("GET /api/dashboard/stats");
  return new Promise((resolve) => {
    setTimeout(() => {
      const alerts = mockAlerts;
      const stats: DashboardStats = {
        total: alerts.length,
        high: alerts.filter(a => a.priority === "high").length,
        urgent: alerts.filter(a => a.daysUntilRenewal <= 30).length,
        totalValue: alerts.reduce((sum, a) => {
          const value = parseFloat(a.currentValue.replace(/[$,]/g, ""));
          return sum + value;
        }, 0)
      };
      logResponse("GET /api/dashboard/stats", stats);
      resolve(stats);
    }, 300);
  });
}

/**
 * Snooze an alert
 * POST /api/alerts/{alertId}/snooze
 */
export async function snoozeAlert(_alertId: string, _snoozeDays: number): Promise<void> {
  logRequest("POST /api/alerts/{alertId}/snooze", { alertId: _alertId, snoozeDays: _snoozeDays });
  return new Promise((resolve) => {
    setTimeout(() => { logResponse("POST /api/alerts/{alertId}/snooze", { success: true }); resolve(); }, 300);
  });
}

/**
 * Dismiss an alert
 * POST /api/alerts/{alertId}/dismiss
 */
export async function dismissAlert(_alertId: string, _reason: string): Promise<void> {
  logRequest("POST /api/alerts/{alertId}/dismiss", { alertId: _alertId, reason: _reason });
  return new Promise((resolve) => {
    setTimeout(() => { logResponse("POST /api/alerts/{alertId}/dismiss", { success: true }); resolve(); }, 300);
  });
}
