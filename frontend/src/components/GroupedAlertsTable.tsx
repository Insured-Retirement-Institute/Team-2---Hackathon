import { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Search,
  BellOff,
  XCircle,
  TrendingDown,
  Clock,
  DollarSign,
  MoreVertical,
  UserPlus,
  ArrowRight,
  ChevronRight,
  ChevronDown,
  FileText,
} from "lucide-react";
import type { RenewalAlert } from "@/types/alerts";
import { cn } from "@/lib/utils";

interface GroupedAlertsTableProps {
  alerts: RenewalAlert[];
  onSelectAlert: (alert: RenewalAlert) => void;
  onSelectClientAlerts?: (clientName: string, alerts: RenewalAlert[]) => void;
  onSnooze: (alert: RenewalAlert) => void;
  onDismiss: (alert: RenewalAlert) => void;
  onAssign?: (alert: RenewalAlert) => void;
  selectedAlertId?: string;
}

interface ClientAlertGroup {
  clientName: string;
  alerts: RenewalAlert[];
  highestPriority: "high" | "medium" | "low";
  totalValue: number;
  urgentCount: number;
  hasDataException: boolean;
}

export function GroupedAlertsTable({
  alerts,
  onSelectAlert,
  onSelectClientAlerts,
  onSnooze,
  onDismiss,
  onAssign,
  selectedAlertId,
}: GroupedAlertsTableProps) {
  const [expandedClients, setExpandedClients] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCarrier, setFilterCarrier] = useState("all");
  const [filterPriority, setFilterPriority] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");

  const carriers = Array.from(new Set(alerts.map((a) => a.carrier)));

  const filteredAlerts = alerts.filter((alert) => {
    const matchesSearch =
      alert.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      alert.policyId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCarrier = filterCarrier === "all" || alert.carrier === filterCarrier;
    const matchesPriority = filterPriority === "all" || alert.priority === filterPriority;
    const matchesStatus = filterStatus === "all" || alert.status === filterStatus;
    return matchesSearch && matchesCarrier && matchesPriority && matchesStatus;
  });

  const clientGroups: ClientAlertGroup[] = Object.values(
    filteredAlerts.reduce(
      (acc, alert) => {
        if (!acc[alert.clientName]) {
          acc[alert.clientName] = {
            clientName: alert.clientName,
            alerts: [],
            highestPriority: "low" as const,
            totalValue: 0,
            urgentCount: 0,
            hasDataException: false,
          };
        }
        const group = acc[alert.clientName];
        group.alerts.push(alert);

        const priorityOrder = { high: 0, medium: 1, low: 2 };
        if (priorityOrder[alert.priority] < priorityOrder[group.highestPriority]) {
          group.highestPriority = alert.priority;
        }

        const value = parseFloat(alert.currentValue.replace(/[$,]/g, "")) || 0;
        group.totalValue += value;

        if (alert.daysUntilRenewal <= 30) {
          group.urgentCount++;
        }
        if (alert.hasDataException) {
          group.hasDataException = true;
        }

        return acc;
      },
      {} as Record<string, ClientAlertGroup>
    )
  );

  const sortedClientGroups = [...clientGroups].sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    if (priorityOrder[a.highestPriority] !== priorityOrder[b.highestPriority]) {
      return priorityOrder[a.highestPriority] - priorityOrder[b.highestPriority];
    }
    return b.urgentCount - a.urgentCount;
  });

  const toggleClientExpanded = (clientName: string) => {
    const newExpanded = new Set(expandedClients);
    if (newExpanded.has(clientName)) {
      newExpanded.delete(clientName);
    } else {
      newExpanded.add(clientName);
    }
    setExpandedClients(newExpanded);
  };

  const getPriorityColor = (priority: "high" | "medium" | "low") => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-700 border-red-300";
      case "medium":
        return "bg-amber-100 text-amber-700 border-amber-300";
      case "low":
        return "bg-slate-100 text-slate-700 border-slate-300";
    }
  };

  const getAlertTypeBadge = (alertType: RenewalAlert["alertType"]) => {
    switch (alertType) {
      case "replacement_recommended":
        return { label: "Replacement", color: "bg-red-50 text-red-700 border-red-300" };
      case "missing_info":
        return { label: "Missing Info", color: "bg-red-50 text-red-700 border-red-300" };
      case "suitability_review":
        return { label: "Suitability", color: "bg-purple-50 text-purple-700 border-purple-300" };
      case "income_planning":
        return { label: "Income", color: "bg-amber-50 text-amber-700 border-amber-300" };
      case "replacement_opportunity":
        return { label: "Replacement", color: "bg-red-50 text-red-700 border-red-300" };
      default:        return { label: "Review", color: "bg-slate-100 text-slate-700 border-slate-300" };
    }
  };

  const getRateDrop = (current: string, renewal: string) => {
    const currentNum = parseFloat(current);
    const renewalNum = parseFloat(renewal);
    return ((renewalNum - currentNum) / currentNum * 100).toFixed(1);
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search by client name or policy ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 h-11 bg-slate-50 border-slate-200 focus:bg-white"
            />
          </div>
          <Select value={filterCarrier} onValueChange={setFilterCarrier}>
            <SelectTrigger className="w-[180px] h-11 bg-slate-50">
              <SelectValue placeholder="All Carriers" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Carriers</SelectItem>
              {carriers.map((carrier) => (
                <SelectItem key={carrier} value={carrier}>
                  {carrier}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={filterPriority} onValueChange={setFilterPriority}>
            <SelectTrigger className="w-[160px] h-11 bg-slate-50">
              <SelectValue placeholder="All Priorities" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              <SelectItem value="high">High Priority</SelectItem>
              <SelectItem value="medium">Medium Priority</SelectItem>
              <SelectItem value="low">Low Priority</SelectItem>
            </SelectContent>
          </Select>
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-[160px] h-11 bg-slate-50">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="reviewed">Reviewed</SelectItem>
              <SelectItem value="snoozed">Snoozed</SelectItem>
              <SelectItem value="dismissed">Dismissed</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between text-sm text-slate-600 px-1">
        <span>
          {sortedClientGroups.length} {sortedClientGroups.length === 1 ? "client" : "clients"} with{" "}
          {filteredAlerts.length} {filteredAlerts.length === 1 ? "alert" : "alerts"}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            if (expandedClients.size === sortedClientGroups.length) {
              setExpandedClients(new Set());
            } else {
              setExpandedClients(new Set(sortedClientGroups.map((g) => g.clientName)));
            }
          }}
          className="text-blue-600 hover:text-blue-700 h-8"
        >
          {expandedClients.size === sortedClientGroups.length ? "Collapse All" : "Expand All"}
        </Button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <Table>
          <colgroup>
            <col className="w-[40px]" />
            <col className="w-[22%]" />
            <col className="w-[12%]" />
            <col className="w-[9%]" />
            <col className="w-[10%]" />
            <col className="w-[13%]" />
            <col className="w-[10%]" />
            <col className="w-[9%]" />
            <col className="w-[12%]" />
          </colgroup>
          <TableHeader>
            <TableRow className="bg-gradient-to-r from-slate-50 to-slate-100 border-b-2 border-slate-200">
              <TableHead className="font-semibold text-slate-700 w-[40px]"></TableHead>
              <TableHead className="font-semibold text-slate-700 w-[22%]">Client / Alert</TableHead>
              <TableHead className="font-semibold text-slate-700 w-[12%]">Alert Type</TableHead>
              <TableHead className="font-semibold text-slate-700 w-[9%]">Renewal</TableHead>
              <TableHead className="font-semibold text-slate-700 w-[10%]">Timeline</TableHead>
              <TableHead className="font-semibold text-slate-700 w-[13%]">Impact</TableHead>
              <TableHead className="font-semibold text-slate-700 w-[10%]">Value</TableHead>
              <TableHead className="font-semibold text-slate-700 w-[9%]">Priority</TableHead>
              <TableHead className="font-semibold text-slate-700 w-[12%] text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedClientGroups.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-12 text-slate-500">
                  <div className="flex flex-col items-center gap-2">
                    <Search className="h-8 w-8 text-slate-300" />
                    <p>No alerts found</p>
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              sortedClientGroups.flatMap((group) => {
                const isExpanded = expandedClients.has(group.clientName);
                const totalAlerts = group.alerts.length;

                const groupRow = (
                  <TableRow
                    key={`group-${group.clientName}`}
                    onClick={() => toggleClientExpanded(group.clientName)}
                    className={cn(
                      "cursor-pointer transition-all hover:bg-blue-50 border-b-2 border-slate-200 bg-slate-50/50 font-medium",
                      group.urgentCount > 0 && "border-l-4 border-l-red-500"
                    )}
                  >
                    <TableCell className="py-3">
                      {isExpanded ? (
                        <ChevronDown className="h-5 w-5 text-slate-600" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-slate-600" />
                      )}
                    </TableCell>

                    <TableCell className="py-3">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900">{group.clientName}</span>
                        <Badge
                          variant="outline"
                          className="bg-blue-50 text-blue-700 border-blue-300 text-xs px-2"
                        >
                          {totalAlerts} {totalAlerts === 1 ? "alert" : "alerts"}
                        </Badge>
                      </div>
                    </TableCell>

                    <TableCell className="py-3">
                      <div className="flex gap-1 flex-wrap">
                        {Array.from(new Set(group.alerts.map((a) => getAlertTypeBadge(a.alertType).label))).map(
                          (label, idx) => {
                            const alertWithLabel = group.alerts.find(
                              (a) => getAlertTypeBadge(a.alertType).label === label
                            );
                            const badge = alertWithLabel
                              ? getAlertTypeBadge(alertWithLabel.alertType)
                              : { label, color: "bg-slate-100 text-slate-700 border-slate-300" };
                            return (
                              <Badge
                                key={idx}
                                variant="outline"
                                className={`${badge.color} text-xs px-2 py-0.5`}
                              >
                                {badge.label}
                              </Badge>
                            );
                          }
                        )}
                      </div>
                    </TableCell>

                    <TableCell className="py-3">
                      <div className="text-sm text-slate-700">
                        {group.alerts.length > 0 && group.alerts[0].renewalDate}
                      </div>
                    </TableCell>

                    <TableCell className="py-3">
                      {group.urgentCount > 0 && (
                        <div className="flex items-center gap-2">
                          <Clock className="h-4 w-4 text-red-500" />
                          <span className="text-sm font-bold text-red-700">
                            {group.urgentCount} urgent
                          </span>
                        </div>
                      )}
                    </TableCell>

                    <TableCell className="py-3">
                      <div className="text-sm text-slate-600">
                        {group.alerts.filter((a) => a.isMinRate).length > 0 && (
                          <Badge className="bg-red-600 text-white text-xs px-2 py-0.5">
                            {group.alerts.filter((a) => a.isMinRate).length} at MIN
                          </Badge>
                        )}
                      </div>
                    </TableCell>

                    <TableCell className="py-3">
                      <div className="flex items-center gap-1.5">
                        <DollarSign className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-bold text-slate-900">
                          ${group.totalValue.toLocaleString()}
                        </span>
                      </div>
                    </TableCell>

                    <TableCell className="py-3">
                      <Badge
                        variant="outline"
                        className={`${getPriorityColor(group.highestPriority)} font-semibold uppercase text-xs px-3 py-1`}
                      >
                        {group.highestPriority}
                      </Badge>
                    </TableCell>

                    <TableCell className="py-3">
                      <div className="flex items-center justify-end gap-2">
                        {totalAlerts > 1 && onSelectClientAlerts ? (
                          <Button
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectClientAlerts(group.clientName, group.alerts);
                            }}
                            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white h-9 w-[120px] font-semibold shadow-md text-xs"
                          >
                            <ArrowRight className="h-4 w-4 mr-1.5" />
                            Review
                          </Button>
                        ) : totalAlerts === 1 ? (
                          <Button
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              onSelectAlert(group.alerts[0]);
                            }}
                            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white h-9 w-[120px] font-semibold shadow-md text-xs"
                          >
                            <ArrowRight className="h-4 w-4 mr-1.5" />
                            Review
                          </Button>
                        ) : (
                          <span className="text-xs text-slate-500">Click to expand</span>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                );

                const alertRows = isExpanded
                  ? group.alerts.map((alert) => {
                      const rateDrop = getRateDrop(alert.currentRate, alert.renewalRate);
                      const isUrgent = alert.daysUntilRenewal <= 30;
                      const alertTypeBadge = getAlertTypeBadge(alert.alertType);

                      return (
                        <TableRow
                          key={alert.id}
                          onClick={() => onSelectAlert(alert)}
                          className={cn(
                            "cursor-pointer transition-all hover:bg-blue-50 border-b border-slate-100 bg-white",
                            selectedAlertId === alert.id && "bg-blue-50",
                            alert.status === "dismissed" && "opacity-50"
                          )}
                        >
                          <TableCell className="py-3 pl-12"></TableCell>

                          <TableCell className="py-3">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4 text-slate-400" />
                                <span className="text-sm font-mono text-slate-700">
                                  {alert.policyId}
                                </span>
                              </div>
                              <div className="text-xs text-slate-500">{alert.carrier}</div>
                              {alert.alertDescription && (
                                <div className="text-xs text-slate-600 italic">
                                  {alert.alertDescription}
                                </div>
                              )}
                            </div>
                          </TableCell>

                          <TableCell className="py-3">
                            <Badge
                              variant="outline"
                              className={`${alertTypeBadge.color} text-xs px-2 py-0.5`}
                            >
                              {alertTypeBadge.label}
                            </Badge>
                          </TableCell>

                          <TableCell className="py-3">
                            <div className="text-sm text-slate-700">{alert.renewalDate}</div>
                          </TableCell>

                          <TableCell className="py-3">
                            <div className="flex items-center gap-2">
                              <Clock
                                className={`h-3.5 w-3.5 ${isUrgent ? "text-red-500" : "text-amber-500"}`}
                              />
                              <div
                                className={`text-sm font-bold ${isUrgent ? "text-red-700" : "text-slate-700"}`}
                              >
                                {alert.daysUntilRenewal} days
                              </div>
                            </div>
                          </TableCell>

                          <TableCell className="py-3">
                            <div className="space-y-1">
                              <div className="flex items-center gap-2">
                                <TrendingDown className="h-3.5 w-3.5 text-red-500" />
                                <span className="text-sm font-bold text-red-700">{rateDrop}%</span>
                                {alert.isMinRate && (
                                  <Badge className="bg-red-600 text-white text-xs px-1.5 py-0">
                                    MIN
                                  </Badge>
                                )}
                              </div>
                              <div className="text-xs text-slate-500">
                                {alert.currentRate} → {alert.renewalRate}
                              </div>
                            </div>
                          </TableCell>

                          <TableCell className="py-3">
                            <div className="flex items-center gap-1.5">
                              <DollarSign className="h-4 w-4 text-green-600" />
                              <span className="text-sm font-bold text-slate-900">
                                {alert.currentValue}
                              </span>
                            </div>
                          </TableCell>

                          <TableCell className="py-3">
                            <Badge
                              variant="outline"
                              className={`${getPriorityColor(alert.priority)} font-semibold uppercase text-xs px-2 py-0.5`}
                            >
                              {alert.priority}
                            </Badge>
                          </TableCell>

                          <TableCell className="py-3">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onSelectAlert(alert);
                                }}
                                disabled={alert.status === "dismissed"}
                                className="bg-blue-600 hover:bg-blue-700 text-white h-9 px-4 font-semibold shadow-md text-xs"
                              >
                                <ArrowRight className="h-4 w-4 mr-1.5" />
                                Review
                              </Button>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={(e) => e.stopPropagation()}
                                    disabled={alert.status === "dismissed"}
                                    className="h-9 w-9 p-0 border-slate-300 hover:bg-slate-100"
                                  >
                                    <MoreVertical className="h-3.5 w-3.5 text-slate-600" />
                                    <span className="sr-only">More actions</span>
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="w-44">
                                  <DropdownMenuItem
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      onSnooze(alert);
                                    }}
                                    className="cursor-pointer"
                                  >
                                    <BellOff className="h-4 w-4 mr-2 text-slate-600" />
                                    Snooze Alert
                                  </DropdownMenuItem>
                                  {onAssign && (
                                    <DropdownMenuItem
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        onAssign(alert);
                                      }}
                                      className="cursor-pointer"
                                    >
                                      <UserPlus className="h-4 w-4 mr-2 text-blue-600" />
                                      Assign / Follow-up
                                    </DropdownMenuItem>
                                  )}
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      onDismiss(alert);
                                    }}
                                    className="cursor-pointer text-red-600"
                                  >
                                    <XCircle className="h-4 w-4 mr-2" />
                                    Dismiss Alert
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  : [];

                return [groupRow, ...alertRows];
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
