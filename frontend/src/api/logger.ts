/* eslint-disable no-console */
const ENABLED = true; // flip to false to silence

export function logRequest(endpoint: string, data?: unknown) {
  if (!ENABLED) return;
  console.log(`%c[API REQ] ${endpoint}`, "color: #3b82f6; font-weight: bold", data ?? "");
}

export function logResponse(endpoint: string, data: unknown) {
  if (!ENABLED) return;
  console.log(`%c[API RES] ${endpoint}`, "color: #10b981; font-weight: bold", data);
}
