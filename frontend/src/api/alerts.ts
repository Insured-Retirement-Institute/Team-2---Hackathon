import type { RenewalAlert, DashboardStats } from "@/types/alerts";
import { mockAlerts } from "./mock/alerts";

/**
 * API Service Layer
 * Currently returns mock data - ready to be replaced with real API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

/**
 * Fetch all renewal alerts
 * GET /api/alerts
 */
export async function fetchAlerts(): Promise<RenewalAlert[]> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/alerts`);
  // return response.json();
  
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockAlerts), 300);
  });
}

/**
 * Fetch dashboard statistics
 * GET /api/dashboard/stats
 */
export async function fetchDashboardStats(): Promise<DashboardStats> {
  // TODO: Replace with real API call
  // const response = await fetch(`${API_BASE_URL}/dashboard/stats`);
  // return response.json();
  
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
      resolve(stats);
    }, 300);
  });
}

/**
 * Snooze an alert
 * POST /api/alerts/{alertId}/snooze
 */
export async function snoozeAlert(alertId: string, snoozeDays: number): Promise<void> {
  // TODO: Replace with real API call
  // await fetch(`${API_BASE_URL}/alerts/${alertId}/snooze`, {
  //   method: 'POST',
  //   body: JSON.stringify({ snoozeDays })
  // });
  
  return new Promise((resolve) => {
    setTimeout(() => resolve(), 300);
  });
}

/**
 * Dismiss an alert
 * POST /api/alerts/{alertId}/dismiss
 */
export async function dismissAlert(alertId: string, reason: string): Promise<void> {
  // TODO: Replace with real API call
  // await fetch(`${API_BASE_URL}/alerts/${alertId}/dismiss`, {
  //   method: 'POST',
  //   body: JSON.stringify({ reason })
  // });
  
  return new Promise((resolve) => {
    setTimeout(() => resolve(), 300);
  });
}
