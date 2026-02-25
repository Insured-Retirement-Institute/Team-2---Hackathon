import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ArrowLeft, ShieldCheck } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  fetchResponsibleAIEvents,
  fetchResponsibleAIStats,
  fetchResponsibleAIEventById,
  type AgentRunEventRow,
  type ResponsibleAIStats,
} from "@/api/responsible-ai";
import { Toaster, toast } from "sonner";

const DAYS_OPTIONS = [
  { label: "Last 7 days", days: 7 },
  { label: "Last 30 days", days: 30 },
];

function toISO(date: Date) {
  return date.toISOString().slice(0, 19) + "Z";
}

export function ResponsibleAIDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<ResponsibleAIStats | null>(null);
  const [events, setEvents] = useState<AgentRunEventRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [agentFilter, setAgentFilter] = useState<string>("");
  const [detailEvent, setDetailEvent] = useState<AgentRunEventRow | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fromDate = new Date();
  fromDate.setDate(fromDate.getDate() - days);
  const toDate = new Date();
  const fromStr = toISO(fromDate);
  const toStr = toISO(toDate);

  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchResponsibleAIStats({
        from_date: fromStr,
        to_date: toStr,
      });
      setStats(data);
    } catch {
      toast.error("Failed to load Responsible AI stats");
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, [fromStr, toStr]);

  const loadEvents = useCallback(async () => {
    try {
      setEventsLoading(true);
      const params: Parameters<typeof fetchResponsibleAIEvents>[0] = {
        from_date: fromStr,
        to_date: toStr,
        limit: 100,
        offset: 0,
      };
      if (agentFilter) params.agent_id = agentFilter;
      const data = await fetchResponsibleAIEvents(params);
      setEvents(data.events);
    } catch {
      toast.error("Failed to load events");
      setEvents([]);
    } finally {
      setEventsLoading(false);
    }
  }, [fromStr, toStr, agentFilter]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  const openDetail = async (eventId: string) => {
    setDetailLoading(true);
    setDetailEvent(null);
    try {
      const event = await fetchResponsibleAIEventById(eventId);
      setDetailEvent(event);
    } catch {
      toast.error("Failed to load event detail");
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" onClick={() => navigate("/")}>
                <ArrowLeft className="h-4 w-4 mr-1" /> Back
              </Button>
              <div className="h-10 w-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                <ShieldCheck className="h-6 w-6 text-emerald-700" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">
                  Responsible AI Dashboard
                </h1>
                <p className="text-sm text-slate-600">
                  Audit runs, explainability, and compliance
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <select
                className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
              >
                {DAYS_OPTIONS.map((o) => (
                  <option key={o.days} value={o.days}>
                    {o.label}
                  </option>
                ))}
              </select>
              <select
                className="rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                value={agentFilter}
                onChange={(e) => setAgentFilter(e.target.value)}
              >
                <option value="">All agents</option>
                <option value="agent_one">Agent One</option>
                <option value="agent_two">Agent Two</option>
                <option value="agent_three">Agent Three</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-8 space-y-8">
        {/* Overview cards */}
        <section>
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            Overview
          </h2>
          {loading ? (
            <div className="text-slate-600">Loading stats...</div>
          ) : stats ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <p className="text-sm text-slate-600">Total runs</p>
                <p className="text-2xl font-bold text-slate-900">
                  {stats.total_runs}
                </p>
              </div>
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <p className="text-sm text-slate-600">Success rate</p>
                <p className="text-2xl font-bold text-slate-900">
                  {stats.success_rate.toFixed(1)}%
                </p>
              </div>
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <p className="text-sm text-slate-600">
                  Explainability coverage (Agent Two)
                </p>
                <p className="text-2xl font-bold text-slate-900">
                  {stats.explainability_coverage_pct.toFixed(1)}%
                </p>
              </div>
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <p className="text-sm text-slate-600">Guardrail triggered</p>
                <p className="text-2xl font-bold text-slate-900">
                  {stats.guardrail_triggered_count}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-slate-600">
              No stats available. Ensure the API and database are configured.
            </p>
          )}
        </section>

        {/* By agent */}
        {stats && (
          <section>
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              By agent
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <p className="font-medium text-slate-900">Agent One</p>
                <p className="text-sm text-slate-600">
                  {stats.agent_one_runs} runs
                </p>
              </div>
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <p className="font-medium text-slate-900">Agent Two</p>
                <p className="text-sm text-slate-600">
                  {stats.agent_two_runs} runs,{" "}
                  {stats.agent_two_with_explanation} with explanation
                </p>
              </div>
              <div className="bg-white rounded-lg border border-slate-200 p-4">
                <p className="font-medium text-slate-900">Agent Three</p>
                <p className="text-sm text-slate-600">
                  {stats.agent_three_runs} runs
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Event list */}
        <section>
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            Recent events
          </h2>
          {eventsLoading ? (
            <div className="text-slate-600">Loading events...</div>
          ) : (
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[140px]">Timestamp</TableHead>
                    <TableHead>Agent</TableHead>
                    <TableHead>Success</TableHead>
                    <TableHead className="max-w-[200px]">Explanation</TableHead>
                    <TableHead>Validation</TableHead>
                    <TableHead>Guardrail</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {events.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={7}
                        className="text-slate-600 text-center py-8"
                      >
                        No events in this range.
                      </TableCell>
                    </TableRow>
                  ) : (
                    events.map((ev) => (
                      <TableRow key={ev.event_id}>
                        <TableCell className="text-slate-600 text-sm">
                          {ev.timestamp
                            ? new Date(ev.timestamp).toLocaleString()
                            : "—"}
                        </TableCell>
                        <TableCell>{ev.agent_id}</TableCell>
                        <TableCell>
                          <Badge
                            variant={ev.success ? "default" : "destructive"}
                          >
                            {ev.success ? "OK" : "Failed"}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate text-slate-600">
                          {ev.explanation_summary ?? "—"}
                        </TableCell>
                        <TableCell>
                          {ev.input_validation_passed == null
                            ? "—"
                            : ev.input_validation_passed
                              ? "Yes"
                              : "No"}
                        </TableCell>
                        <TableCell>
                          {ev.guardrail_triggered == null
                            ? "—"
                            : ev.guardrail_triggered
                              ? "Yes"
                              : "No"}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openDetail(ev.event_id)}
                          >
                            Detail
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </section>
      </div>

      {/* Event detail modal */}
      <Dialog
        open={detailEvent !== null || detailLoading}
        onOpenChange={(open) => {
          if (!open) setDetailEvent(null);
        }}
      >
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Event detail</DialogTitle>
          </DialogHeader>
          {detailLoading ? (
            <p className="text-slate-600">Loading...</p>
          ) : detailEvent ? (
            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <span className="text-slate-600">Event ID</span>
                <span className="font-mono">{detailEvent.event_id}</span>
                <span className="text-slate-600">Timestamp</span>
                <span>
                  {detailEvent.timestamp
                    ? new Date(detailEvent.timestamp).toLocaleString()
                    : "—"}
                </span>
                <span className="text-slate-600">Agent</span>
                <span>{detailEvent.agent_id}</span>
                <span className="text-slate-600">Success</span>
                <span>{detailEvent.success ? "Yes" : "No"}</span>
                <span className="text-slate-600">Validation passed</span>
                <span>
                  {detailEvent.input_validation_passed == null
                    ? "—"
                    : detailEvent.input_validation_passed
                      ? "Yes"
                      : "No"}
                </span>
                {detailEvent.error_message && (
                  <>
                    <span className="text-slate-600">Error</span>
                    <span className="text-red-600">
                      {detailEvent.error_message}
                    </span>
                  </>
                )}
              </div>
              {detailEvent.explanation_summary && (
                <>
                  <p className="text-slate-600 font-medium">Explanation</p>
                  <p className="text-slate-900">
                    {detailEvent.explanation_summary}
                  </p>
                </>
              )}
              {(detailEvent.data_sources_used?.length ?? 0) > 0 && (
                <>
                  <p className="text-slate-600 font-medium">
                    Data sources used
                  </p>
                  <ul className="list-disc pl-4 text-slate-900">
                    {detailEvent.data_sources_used!.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </>
              )}
              {(detailEvent.choice_criteria?.length ?? 0) > 0 && (
                <>
                  <p className="text-slate-600 font-medium">Choice criteria</p>
                  <ul className="list-disc pl-4 text-slate-900">
                    {detailEvent.choice_criteria!.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </>
              )}
              {detailEvent.input_summary &&
                Object.keys(detailEvent.input_summary).length > 0 && (
                  <>
                    <p className="text-slate-600 font-medium">Input summary</p>
                    <pre className="bg-slate-100 rounded p-2 text-xs overflow-x-auto">
                      {JSON.stringify(detailEvent.input_summary, null, 2)}
                    </pre>
                  </>
                )}
              {detailEvent.payload && (
                <>
                  <p className="text-slate-600 font-medium">
                    Full payload (Agent Two)
                  </p>
                  <pre className="bg-slate-100 rounded p-2 text-xs overflow-x-auto max-h-60 overflow-y-auto">
                    {JSON.stringify(detailEvent.payload.payload, null, 2)}
                  </pre>
                </>
              )}
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
      <Toaster />
    </div>
  );
}
