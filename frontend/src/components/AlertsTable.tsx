import type { RenewalAlert } from "@/types/alerts";
import { Badge } from "@/components/ui/badge";
import { AlertCircle } from "lucide-react";

interface AlertsTableProps {
  alerts: RenewalAlert[];
}

export function AlertsTable({ alerts }: AlertsTableProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-50 text-red-700 border-red-200";
      case "medium":
        return "bg-orange-50 text-orange-700 border-orange-200";
      case "low":
        return "bg-blue-50 text-blue-700 border-blue-200";
      default:
        return "bg-slate-50 text-slate-700 border-slate-200";
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl shadow-lg overflow-hidden">
      <div className="p-6 border-b border-slate-200">
        <h3 className="text-xl font-bold text-slate-900">Renewal Alerts</h3>
        <p className="text-sm text-slate-600 mt-1">
          {alerts.length} active alerts requiring attention
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Client
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Policy ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Carrier
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Current Value
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Renewal Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Rate Change
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {alerts.map((alert) => (
              <tr
                key={alert.id}
                className="hover:bg-slate-50 transition-colors cursor-pointer"
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    {alert.hasDataException && (
                      <AlertCircle className="h-4 w-4 text-amber-500 mr-2" />
                    )}
                    <span className="text-sm font-medium text-slate-900">
                      {alert.clientName}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                  {alert.policyId}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                  {alert.carrier}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                  {alert.currentValue}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`text-sm ${alert.daysUntilRenewal <= 15 ? 'text-red-600 font-semibold' : 'text-slate-600'}`}>
                    {alert.renewalDate}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm">
                    <div className="text-slate-600">{alert.currentRate} → {alert.renewalRate}</div>
                    {alert.isMinRate && (
                      <Badge variant="outline" className="mt-1 bg-red-50 text-red-700 border-red-200 text-xs">
                        Min Rate
                      </Badge>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Badge
                    variant="outline"
                    className={getPriorityColor(alert.priority)}
                  >
                    {alert.priority.toUpperCase()}
                  </Badge>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Badge variant="outline" className="bg-slate-50 text-slate-700 border-slate-200">
                    {alert.status}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
