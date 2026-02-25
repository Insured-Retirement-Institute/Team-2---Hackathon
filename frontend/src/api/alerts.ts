import type { RenewalAlert, DashboardStats } from "@/types/alerts";
import { logRequest, logResponse } from "./logger";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Fetch all renewal alerts
 * GET /api/alerts
 */
export async function fetchAlerts(): Promise<RenewalAlert[]> {
  logRequest("GET /api/alerts");
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
  const res = await fetch(`${API_BASE_URL}/alerts/${alertId}/dismiss`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason }),
  });
  if (!res.ok) throw new Error(`Failed to dismiss alert: ${res.statusText}`);
  const r = await res.json();
  logResponse("POST /api/alerts/{alertId}/dismiss", r);
}
