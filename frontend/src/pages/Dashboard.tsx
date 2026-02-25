import { useState, useEffect } from "react";
import { useChatContext } from "@/hooks/useChatContext";
import { useNavigate, Link } from "react-router-dom";
import { LayoutDashboard, ShieldCheck } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { StatsCards } from "@/components/StatsCards";
import { GroupedAlertsTable } from "@/components/GroupedAlertsTable";
import type { RenewalAlert, DashboardStats } from "@/types/alerts";
import { fetchAlerts, fetchDashboardStats } from "@/api/alerts";
import { Toaster, toast } from "sonner";

export function Dashboard() {
  const navigate = useNavigate();
  const { sendContext } = useChatContext();
  const [alerts, setAlerts] = useState<RenewalAlert[]>([]);
  const [stats, setStats] = useState<DashboardStats>({ total: 0, high: 0, urgent: 0, totalValue: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [alertsData, statsData] = await Promise.all([fetchAlerts(), fetchDashboardStats()]);
      setAlerts(alertsData);
      setStats(statsData);
    } catch {
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAlert = (alert: RenewalAlert) => {
    sendContext({ page: `/alerts/${alert.id}`, alertId: alert.id, activeTab: "overview", clientName: alert.clientName, policyId: alert.policyId });
    navigate(`/alerts/${alert.id}`);
  };

  const handleSelectClientAlerts = (_clientName: string, alerts: RenewalAlert[]) => {
    navigate(`/alerts/${alerts[0].id}`);
  };

  const handleSnooze = (alert: RenewalAlert) => {
    toast.info(`Snooze alert for ${alert.clientName}`);
  };

  const handleDismiss = (alert: RenewalAlert) => {
    toast.info(`Dismiss alert for ${alert.clientName}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <LayoutDashboard className="h-6 w-6 text-blue-700" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">IRI Dashboard</h1>
                <p className="text-sm text-slate-600">Annuity Renewal Intelligence</p>
              </div>
            </div>
            <Link
              to="/admin/responsible-ai"
              className="inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
            >
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              Responsible AI
            </Link>
          </div>
        </div>
      </div>

      <Separator />

      <div className="max-w-7xl mx-auto px-8 py-8 space-y-8">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">My Dashboard</h2>
          <p className="text-base text-slate-600 mt-2">Key portfolio metrics and alerts at a glance</p>
        </div>

        <StatsCards stats={stats} />

        <GroupedAlertsTable
          alerts={alerts}
          onSelectAlert={handleSelectAlert}
          onSelectClientAlerts={handleSelectClientAlerts}
          onSnooze={handleSnooze}
          onDismiss={handleDismiss}
        />
      </div>

      <Toaster position="top-right" richColors />
    </div>
  );
}
