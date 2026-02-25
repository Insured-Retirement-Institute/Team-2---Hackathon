import { Target, AlertCircle, Clock, DollarSign } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { DashboardStats } from "@/types/alerts";

interface StatsCardsProps {
  stats: DashboardStats;
}

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-4 gap-6">
      <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
            <Target className="h-6 w-6 text-blue-700" />
          </div>
          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 font-semibold">
            Total
          </Badge>
        </div>
        <div className="text-3xl font-bold text-slate-900 mb-1">{stats.total}</div>
        <div className="text-sm text-slate-600">Active Alerts</div>
      </div>

      <div className="bg-gradient-to-br from-white to-red-50 border border-red-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-red-100 to-red-200 flex items-center justify-center">
            <AlertCircle className="h-6 w-6 text-red-700" />
          </div>
          <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200 font-semibold">
            Critical
          </Badge>
        </div>
        <div className="text-3xl font-bold text-red-700 mb-1">{stats.high}</div>
        <div className="text-sm text-slate-600">High Priority</div>
      </div>

      <div className="bg-gradient-to-br from-white to-orange-50 border border-orange-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-orange-100 to-orange-200 flex items-center justify-center">
            <Clock className="h-6 w-6 text-orange-700" />
          </div>
          <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200 font-semibold">
            Urgent
          </Badge>
        </div>
        <div className="text-3xl font-bold text-orange-700 mb-1">{stats.urgent}</div>
        <div className="text-sm text-slate-600">Within 30 Days</div>
      </div>

      <div className="bg-gradient-to-br from-white to-green-50 border border-green-200 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-shadow">
        <div className="flex items-start justify-between mb-4">
          <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-green-100 to-green-200 flex items-center justify-center">
            <DollarSign className="h-6 w-6 text-green-700" />
          </div>
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 font-semibold">
            AUM
          </Badge>
        </div>
        <div className="text-3xl font-bold text-green-700 mb-1">
          ${(stats.totalValue / 1000000).toFixed(1)}M
        </div>
        <div className="text-sm text-slate-600">Total Value</div>
      </div>
    </div>
  );
}
