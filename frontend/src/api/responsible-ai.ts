// In dev, use /api-backend so Vite proxies to the API without conflicting with the SPA route /admin/responsible-ai
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? "/api-backend" : "");

export interface AgentRunEventRow {
  id: number;
  event_id: string;
  timestamp: string;
  agent_id: string;
  run_id: string | null;
  client_id_scope: string | null;
  input_summary: Record<string, unknown>;
  success: boolean;
  error_message: string | null;
  explanation_summary: string | null;
  data_sources_used: string[] | null;
  choice_criteria: string[] | null;
  input_validation_passed: boolean | null;
  guardrail_triggered: boolean | null;
  payload_ref: string | null;
  payload?: {
    id: string;
    run_id: string;
    created_at: string;
    client_id: string;
    payload: Record<string, unknown>;
  } | null;
}

export interface ResponsibleAIStats {
  from_date: string;
  to_date: string;
  total_runs: number;
  success_count: number;
  success_rate: number;
  agent_one_runs: number;
  agent_two_runs: number;
  agent_three_runs: number;
  agent_two_with_explanation: number;
  explainability_coverage_pct: number;
  guardrail_triggered_count: number;
}

export async function fetchResponsibleAIEvents(params: {
  agent_id?: string;
  from_date?: string;
  to_date?: string;
  success?: boolean;
  client_id_scope?: string;
  limit?: number;
  offset?: number;
}): Promise<{ events: AgentRunEventRow[] }> {
  const sp = new URLSearchParams();
  if (params.agent_id != null) sp.set("agent_id", params.agent_id);
  if (params.from_date != null) sp.set("from_date", params.from_date);
  if (params.to_date != null) sp.set("to_date", params.to_date);
  if (params.success != null) sp.set("success", String(params.success));
  if (params.client_id_scope != null) sp.set("client_id_scope", params.client_id_scope);
  if (params.limit != null) sp.set("limit", String(params.limit));
  if (params.offset != null) sp.set("offset", String(params.offset));
  const url = `${API_BASE}/admin/responsible-ai/events?${sp.toString()}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load events: ${res.status}`);
  return res.json();
}

export async function fetchResponsibleAIStats(params: {
  from_date?: string;
  to_date?: string;
}): Promise<ResponsibleAIStats> {
  const sp = new URLSearchParams();
  if (params.from_date != null) sp.set("from_date", params.from_date);
  if (params.to_date != null) sp.set("to_date", params.to_date);
  const url = `${API_BASE}/admin/responsible-ai/stats?${sp.toString()}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to load stats: ${res.status}`);
  return res.json();
}

export async function fetchResponsibleAIEventById(eventId: string): Promise<AgentRunEventRow> {
  const url = `${API_BASE}/admin/responsible-ai/events/${encodeURIComponent(eventId)}`;
  const res = await fetch(url);
  if (!res.ok) {
    if (res.status === 404) throw new Error("Event not found");
    throw new Error(`Failed to load event: ${res.status}`);
  }
  return res.json();
}
