import React, { useState } from "react";
import {
  Shield,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  TrendingUp,
  TrendingDown,
  Database,
  Zap,
  FileText,
  Eye,
  Clock,
  Users,
  BarChart3,
  AlertCircle,
  Check,
  X,
  ChevronRight,
  ChevronDown,
  Download,
  Filter,
  Search,
  RefreshCcw,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";

// Mock data for AI system health
const generateSystemHealthData = () => {
  const last24Hours = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date();
    hour.setHours(hour.getHours() - (23 - i));
    return {
      time: hour.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      requests: Math.floor(Math.random() * 200) + 150,
      successRate: 95 + Math.random() * 5,
      avgResponseTime: 150 + Math.random() * 100,
      errors: Math.floor(Math.random() * 5),
    };
  });
  return last24Hours;
};

const generateBiasMetrics = () => {
  return [
    {
      category: "Age Distribution",
      actual: 85,
      expected: 90,
      variance: -5,
      status: "warning",
    },
    {
      category: "Gender Parity",
      actual: 98,
      expected: 100,
      variance: -2,
      status: "healthy",
    },
    {
      category: "Product Type Balance",
      actual: 92,
      expected: 95,
      variance: -3,
      status: "healthy",
    },
    {
      category: "Recommendation Diversity",
      actual: 88,
      expected: 90,
      variance: -2,
      status: "healthy",
    },
    {
      category: "Income Level Distribution",
      actual: 75,
      expected: 90,
      variance: -15,
      status: "alert",
    },
    {
      category: "Geographic Distribution",
      actual: 95,
      expected: 95,
      variance: 0,
      status: "healthy",
    },
  ];
};

const generateComplianceMetrics = () => {
  return [
    {
      area: "Suitability Analysis",
      score: 98,
      total: 1247,
      compliant: 1222,
      flagged: 25,
      trend: "up",
    },
    {
      area: "Disclosure Requirements",
      score: 100,
      total: 1247,
      compliant: 1247,
      flagged: 0,
      trend: "stable",
    },
    {
      area: "Documentation Quality",
      score: 96,
      total: 1247,
      compliant: 1197,
      flagged: 50,
      trend: "up",
    },
    {
      area: "Transaction Approval",
      score: 99,
      total: 856,
      compliant: 847,
      flagged: 9,
      trend: "stable",
    },
    {
      area: "Client Consent Records",
      score: 100,
      total: 856,
      compliant: 856,
      flagged: 0,
      trend: "up",
    },
  ];
};

const generateAuditLog = () => {
  const actions = [
    "Recommendation generated",
    "Suitability score calculated",
    "Bias check performed",
    "Compliance scan completed",
    "Product comparison analyzed",
    "Client profile assessed",
    "Transaction validated",
    "Documentation verified",
  ];
  
  const results = ["Success", "Success", "Success", "Warning", "Success", "Flagged"];
  
  return Array.from({ length: 50 }, (_, i) => {
    const timestamp = new Date(Date.now() - i * 120000);
    return {
      id: `AUD-${1000 + i}`,
      timestamp: timestamp.toLocaleString(),
      agent: `Insights Agent ${(i % 3) + 1}`,
      action: actions[Math.floor(Math.random() * actions.length)],
      clientId: `CLT-${Math.floor(Math.random() * 9000) + 1000}`,
      result: results[Math.floor(Math.random() * results.length)],
      biasScore: 90 + Math.floor(Math.random() * 10),
      complianceScore: 95 + Math.floor(Math.random() * 5),
    };
  });
};

const generateRecommendationDistribution = () => {
  return [
    { name: "Renew Current", value: 342, color: "#3b82f6" },
    { name: "1035 Exchange", value: 428, color: "#8b5cf6" },
    { name: "Partial Surrender", value: 156, color: "#06b6d4" },
    { name: "No Action", value: 321, color: "#64748b" },
  ];
};

const generateBiasRadarData = () => {
  return [
    { metric: "Age", score: 85, fullMark: 100 },
    { metric: "Gender", score: 98, fullMark: 100 },
    { metric: "Income", score: 75, fullMark: 100 },
    { metric: "Geography", score: 95, fullMark: 100 },
    { metric: "Product Type", score: 92, fullMark: 100 },
    { metric: "Risk Profile", score: 88, fullMark: 100 },
  ];
};

interface AuditDashboardProps {
  onClose?: () => void;
}

export function AIAuditDashboard({ onClose }: AuditDashboardProps) {
  const [selectedTab, setSelectedTab] = useState<"overview" | "bias" | "compliance" | "audit">("overview");
  const [timeRange, setTimeRange] = useState<"24h" | "7d" | "30d">("24h");
  const [expandedLog, setExpandedLog] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const systemHealth = generateSystemHealthData();
  const biasMetrics = generateBiasMetrics();
  const complianceMetrics = generateComplianceMetrics();
  const auditLog = generateAuditLog();
  const recommendationDist = generateRecommendationDistribution();
  const biasRadar = generateBiasRadarData();

  // Calculate aggregate scores
  const overallBiasScore = Math.round(
    biasMetrics.reduce((sum, m) => sum + m.actual, 0) / biasMetrics.length
  );
  const overallComplianceScore = Math.round(
    complianceMetrics.reduce((sum, m) => sum + m.score, 0) / complianceMetrics.length
  );
  const totalRequests = systemHealth.reduce((sum, h) => sum + h.requests, 0);
  const avgSuccessRate = (
    systemHealth.reduce((sum, h) => sum + h.successRate, 0) / systemHealth.length
  ).toFixed(1);
  const totalErrors = systemHealth.reduce((sum, h) => sum + h.errors, 0);

  const agentStatus = [
    { name: "Insights Agent 1", status: "healthy", uptime: 99.8, requests: 4234, avgLatency: 145 },
    { name: "Insights Agent 2", status: "healthy", uptime: 99.9, requests: 4156, avgLatency: 138 },
    { name: "Insights Agent 3", status: "healthy", uptime: 99.7, requests: 4089, avgLatency: 152 },
    { name: "Compliance Scanner", status: "healthy", uptime: 100, requests: 1247, avgLatency: 89 },
    { name: "Bias Detector", status: "warning", uptime: 98.2, requests: 1247, avgLatency: 203 },
  ];

  const apiEndpoints = [
    { name: "Suitability Analysis API", status: "healthy", uptime: 99.9, calls: 1247, errors: 2 },
    { name: "Product Comparison API", status: "healthy", uptime: 99.8, calls: 3421, errors: 5 },
    { name: "Carrier Rate API", status: "healthy", uptime: 100, calls: 2156, errors: 0 },
    { name: "Client Profile API", status: "healthy", uptime: 99.7, calls: 1893, errors: 4 },
    { name: "Compliance Check API", status: "warning", uptime: 97.3, calls: 1247, errors: 34 },
  ];

  const filteredAuditLog = auditLog.filter(
    (log) =>
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.agent.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.clientId.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col bg-slate-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Shield className="h-6 w-6 text-blue-600" />
              <h1 className="text-xl font-bold text-slate-900">System Audit & Compliance Dashboard</h1>
            </div>
            <p className="text-sm text-slate-600 mt-1">
              Monitor agent health, API status, bias detection, and compliance metrics
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="text-xs">
              <Download className="h-3.5 w-3.5 mr-1.5" />
              Export Report
            </Button>
            <Button variant="outline" size="sm" className="text-xs">
              <RefreshCcw className="h-3.5 w-3.5 mr-1.5" />
              Refresh
            </Button>
            {onClose && (
              <Button variant="ghost" size="sm" onClick={onClose}>
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 mt-4">
          <button
            onClick={() => setSelectedTab("overview")}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              selectedTab === "overview"
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            )}
          >
            Overview
          </button>
          <button
            onClick={() => setSelectedTab("bias")}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              selectedTab === "bias"
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            )}
          >
            Bias Detection
          </button>
          <button
            onClick={() => setSelectedTab("compliance")}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              selectedTab === "compliance"
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            )}
          >
            Compliance
          </button>
          <button
            onClick={() => setSelectedTab("audit")}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
              selectedTab === "audit"
                ? "bg-blue-600 text-white"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            )}
          >
            Audit Log
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {selectedTab === "overview" && (
          <div className="space-y-6">
            {/* Top Metrics */}
            <div className="grid grid-cols-5 gap-4">
              <Card className="p-4 border-2 border-green-200 bg-green-50">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-green-800">Overall Health</p>
                    <p className="text-2xl font-bold text-green-900 mt-1">98.6%</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-600" />
                </div>
                <div className="flex items-center gap-1 mt-2">
                  <TrendingUp className="h-3 w-3 text-green-600" />
                  <span className="text-xs text-green-700">+0.3% vs yesterday</span>
                </div>
              </Card>

              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-slate-600">Total Requests</p>
                    <p className="text-2xl font-bold text-slate-900 mt-1">{totalRequests.toLocaleString()}</p>
                  </div>
                  <Activity className="h-8 w-8 text-blue-600" />
                </div>
                <p className="text-xs text-slate-500 mt-2">Last 24 hours</p>
              </Card>

              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-slate-600">Success Rate</p>
                    <p className="text-2xl font-bold text-slate-900 mt-1">{avgSuccessRate}%</p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-emerald-600" />
                </div>
                <p className="text-xs text-slate-500 mt-2">Avg. over 24h</p>
              </Card>

              <Card className="p-4 border-2 border-amber-200 bg-amber-50">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-amber-800">Bias Score</p>
                    <p className="text-2xl font-bold text-amber-900 mt-1">{overallBiasScore}/100</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-amber-600" />
                </div>
                <div className="flex items-center gap-1 mt-2">
                  <AlertCircle className="h-3 w-3 text-amber-600" />
                  <span className="text-xs text-amber-700">1 alert requiring review</span>
                </div>
              </Card>

              <Card className="p-4 border-2 border-blue-200 bg-blue-50">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-blue-800">Compliance</p>
                    <p className="text-2xl font-bold text-blue-900 mt-1">{overallComplianceScore}%</p>
                  </div>
                  <Shield className="h-8 w-8 text-blue-600" />
                </div>
                <div className="flex items-center gap-1 mt-2">
                  <CheckCircle2 className="h-3 w-3 text-blue-600" />
                  <span className="text-xs text-blue-700">All checks passing</span>
                </div>
              </Card>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-2 gap-6">
              {/* System Performance */}
              <Card className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-900">System Performance (24h)</h3>
                  <Badge variant="outline" className="text-xs">Live</Badge>
                </div>
                <ResponsiveContainer width="100%" height={240}>
                  <AreaChart data={systemHealth}>
                    <defs>
                      <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="time" tick={{ fontSize: 11 }} stroke="#64748b" />
                    <YAxis tick={{ fontSize: 11 }} stroke="#64748b" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "white",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="requests"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      fill="url(#colorRequests)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Card>

              {/* Recommendation Distribution */}
              <Card className="p-5">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Recommendation Distribution</h3>
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie
                      data={recommendationDist}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {recommendationDist.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </div>

            {/* Agent Status */}
            <Card className="p-5">
              <h3 className="text-sm font-semibold text-slate-900 mb-4">Agent Status</h3>
              <div className="space-y-3">
                {agentStatus.map((agent, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          "h-2 w-2 rounded-full",
                          agent.status === "healthy" ? "bg-green-500" : "bg-amber-500"
                        )}
                      />
                      <div>
                        <p className="text-sm font-medium text-slate-900">{agent.name}</p>
                        <p className="text-xs text-slate-500">
                          {agent.requests.toLocaleString()} requests · {agent.avgLatency}ms avg latency
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-xs text-slate-500">Uptime</p>
                        <p className="text-sm font-semibold text-slate-900">{agent.uptime}%</p>
                      </div>
                      <Badge
                        variant={agent.status === "healthy" ? "default" : "secondary"}
                        className={cn(
                          "text-xs",
                          agent.status === "healthy"
                            ? "bg-green-100 text-green-800 hover:bg-green-100"
                            : "bg-amber-100 text-amber-800 hover:bg-amber-100"
                        )}
                      >
                        {agent.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* API Endpoints */}
            <Card className="p-5">
              <h3 className="text-sm font-semibold text-slate-900 mb-4">API Endpoint Health</h3>
              <div className="space-y-3">
                {apiEndpoints.map((api, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          "h-2 w-2 rounded-full",
                          api.status === "healthy" ? "bg-green-500" : "bg-amber-500"
                        )}
                      />
                      <div>
                        <p className="text-sm font-medium text-slate-900">{api.name}</p>
                        <p className="text-xs text-slate-500">
                          {api.calls.toLocaleString()} calls · {api.errors} errors
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-xs text-slate-500">Uptime</p>
                        <p className="text-sm font-semibold text-slate-900">{api.uptime}%</p>
                      </div>
                      <Badge
                        variant={api.status === "healthy" ? "default" : "secondary"}
                        className={cn(
                          "text-xs",
                          api.status === "healthy"
                            ? "bg-green-100 text-green-800 hover:bg-green-100"
                            : "bg-amber-100 text-amber-800 hover:bg-amber-100"
                        )}
                      >
                        {api.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {selectedTab === "bias" && (
          <div className="space-y-6">
            {/* Bias Score Header */}
            <Card className="p-6 border-2 border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <AlertTriangle className="h-6 w-6 text-amber-600" />
                    <h2 className="text-lg font-bold text-slate-900">Bias Detection Analysis</h2>
                  </div>
                  <p className="text-sm text-slate-600 mb-4">
                    Monitoring recommendation fairness across demographic and product categories
                  </p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-amber-900">{overallBiasScore}</span>
                    <span className="text-lg text-amber-700">/100</span>
                    <Badge variant="secondary" className="ml-3 bg-amber-100 text-amber-800">
                      1 Alert Detected
                    </Badge>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 mb-1">Threshold</p>
                  <p className="text-2xl font-bold text-slate-900">85</p>
                  <p className="text-xs text-slate-500 mt-2">Scores below 85 require review</p>
                </div>
              </div>
            </Card>

            <div className="grid grid-cols-2 gap-6">
              {/* Bias Radar Chart */}
              <Card className="p-5">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Fairness Metrics by Category</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={biasRadar}>
                    <PolarGrid stroke="#e2e8f0" />
                    <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12 }} stroke="#64748b" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 11 }} />
                    <Radar
                      name="Current Score"
                      dataKey="score"
                      stroke="#f59e0b"
                      fill="#f59e0b"
                      fillOpacity={0.5}
                      strokeWidth={2}
                    />
                    <Radar
                      name="Target"
                      dataKey="fullMark"
                      stroke="#64748b"
                      fill="#64748b"
                      fillOpacity={0.1}
                      strokeWidth={1}
                      strokeDasharray="5 5"
                    />
                    <Legend />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </Card>

              {/* Detailed Metrics Table */}
              <Card className="p-5">
                <h3 className="text-sm font-semibold text-slate-900 mb-4">Detailed Bias Metrics</h3>
                <div className="space-y-2">
                  {biasMetrics.map((metric, idx) => (
                    <div
                      key={idx}
                      className={cn(
                        "p-3 rounded-lg border",
                        metric.status === "alert"
                          ? "bg-red-50 border-red-200"
                          : metric.status === "warning"
                          ? "bg-amber-50 border-amber-200"
                          : "bg-green-50 border-green-200"
                      )}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium text-slate-900">{metric.category}</p>
                        <Badge
                          variant="secondary"
                          className={cn(
                            "text-xs",
                            metric.status === "alert"
                              ? "bg-red-100 text-red-800"
                              : metric.status === "warning"
                              ? "bg-amber-100 text-amber-800"
                              : "bg-green-100 text-green-800"
                          )}
                        >
                          {metric.status}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-baseline gap-2">
                            <span className="text-lg font-bold text-slate-900">{metric.actual}</span>
                            <span className="text-xs text-slate-500">/ {metric.expected} expected</span>
                          </div>
                          <div className="mt-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                              className={cn(
                                "h-full",
                                metric.status === "alert"
                                  ? "bg-red-500"
                                  : metric.status === "warning"
                                  ? "bg-amber-500"
                                  : "bg-green-500"
                              )}
                              style={{ width: `${metric.actual}%` }}
                            />
                          </div>
                        </div>
                        <div className="ml-4 text-right">
                          <div className="flex items-center gap-1">
                            {metric.variance < 0 ? (
                              <TrendingDown className="h-3 w-3 text-red-500" />
                            ) : (
                              <TrendingUp className="h-3 w-3 text-green-500" />
                            )}
                            <span
                              className={cn(
                                "text-xs font-semibold",
                                metric.variance < 0 ? "text-red-600" : "text-green-600"
                              )}
                            >
                              {metric.variance > 0 ? "+" : ""}
                              {metric.variance}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Action Items */}
            <Card className="p-5 border-2 border-red-200 bg-red-50">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-red-900 mb-2">Action Required</h3>
                  <p className="text-sm text-red-800 mb-3">
                    <strong>Income Level Distribution</strong> is below the acceptable threshold (75/100). This
                    indicates potential bias in recommendations across different income segments.
                  </p>
                  <div className="flex gap-2">
                    <Button size="sm" className="bg-red-600 hover:bg-red-700 text-white text-xs">
                      Review Cases
                    </Button>
                    <Button variant="outline" size="sm" className="text-xs border-red-300 text-red-700">
                      View Details
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {selectedTab === "compliance" && (
          <div className="space-y-6">
            {/* Compliance Score Header */}
            <Card className="p-6 border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <Shield className="h-6 w-6 text-blue-600" />
                    <h2 className="text-lg font-bold text-slate-900">Compliance Monitoring</h2>
                  </div>
                  <p className="text-sm text-slate-600 mb-4">
                    Real-time compliance tracking across all regulatory requirements
                  </p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold text-blue-900">{overallComplianceScore}%</span>
                    <Badge variant="secondary" className="ml-3 bg-green-100 text-green-800">
                      All Checks Passing
                    </Badge>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 mb-1">Minimum Required</p>
                  <p className="text-2xl font-bold text-slate-900">95%</p>
                  <p className="text-xs text-slate-500 mt-2">Currently exceeding threshold</p>
                </div>
              </div>
            </Card>

            {/* Compliance Areas */}
            <div className="grid grid-cols-1 gap-4">
              {complianceMetrics.map((area, idx) => (
                <Card key={idx} className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-sm font-semibold text-slate-900">{area.area}</h3>
                        {area.trend === "up" && <TrendingUp className="h-4 w-4 text-green-500" />}
                      </div>
                      <p className="text-xs text-slate-500">
                        {area.compliant.toLocaleString()} of {area.total.toLocaleString()} transactions compliant
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-slate-900">{area.score}%</p>
                      <Badge
                        variant="secondary"
                        className={cn(
                          "text-xs mt-1",
                          area.score === 100
                            ? "bg-green-100 text-green-800"
                            : area.score >= 95
                            ? "bg-blue-100 text-blue-800"
                            : "bg-amber-100 text-amber-800"
                        )}
                      >
                        {area.score === 100 ? "Perfect" : area.score >= 95 ? "Compliant" : "Review"}
                      </Badge>
                    </div>
                  </div>
                  <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={cn(
                        "h-full",
                        area.score === 100
                          ? "bg-green-500"
                          : area.score >= 95
                          ? "bg-blue-500"
                          : "bg-amber-500"
                      )}
                      style={{ width: `${area.score}%` }}
                    />
                  </div>
                  {area.flagged > 0 && (
                    <div className="mt-3 flex items-center gap-2 text-xs text-amber-700 bg-amber-50 p-2 rounded border border-amber-200">
                      <AlertCircle className="h-4 w-4" />
                      <span>
                        {area.flagged} transaction{area.flagged > 1 ? "s" : ""} flagged for review
                      </span>
                    </div>
                  )}
                </Card>
              ))}
            </div>

            {/* Regulatory Framework */}
            <Card className="p-5">
              <h3 className="text-sm font-semibold text-slate-900 mb-4">Regulatory Framework Adherence</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <p className="text-sm font-semibold text-green-900">FINRA Reg Notice 12-25</p>
                  </div>
                  <p className="text-xs text-green-700">Variable Annuity Exchanges - Compliant</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <p className="text-sm font-semibold text-green-900">SEC Reg Best Interest</p>
                  </div>
                  <p className="text-xs text-green-700">Suitability Requirements - Compliant</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                    <p className="text-sm font-semibold text-green-900">State Insurance Codes</p>
                  </div>
                  <p className="text-xs text-green-700">Replacement Forms - Compliant</p>
                </div>
              </div>
            </Card>
          </div>
        )}

        {selectedTab === "audit" && (
          <div className="space-y-6">
            {/* Search and Filters */}
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search by action, agent, or client ID..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filters
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </Card>

            {/* Audit Log Table */}
            <Card className="p-5">
              <h3 className="text-sm font-semibold text-slate-900 mb-4">
                Audit Trail ({filteredAuditLog.length} records)
              </h3>
              <div className="space-y-2">
                {filteredAuditLog.slice(0, 20).map((log) => (
                  <div
                    key={log.id}
                    className="border border-slate-200 rounded-lg hover:border-blue-300 transition-colors"
                  >
                    <div
                      className="p-3 cursor-pointer"
                      onClick={() => setExpandedLog(expandedLog === log.id ? null : log.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 flex-1">
                          <div
                            className={cn(
                              "h-2 w-2 rounded-full",
                              log.result === "Success"
                                ? "bg-green-500"
                                : log.result === "Warning"
                                ? "bg-amber-500"
                                : "bg-red-500"
                            )}
                          />
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <p className="text-sm font-medium text-slate-900">{log.action}</p>
                              <Badge variant="outline" className="text-xs">
                                {log.agent}
                              </Badge>
                            </div>
                            <p className="text-xs text-slate-500 mt-0.5">
                              {log.timestamp} · Client: {log.clientId}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge
                            variant="secondary"
                            className={cn(
                              "text-xs",
                              log.result === "Success"
                                ? "bg-green-100 text-green-800"
                                : log.result === "Warning"
                                ? "bg-amber-100 text-amber-800"
                                : "bg-red-100 text-red-800"
                            )}
                          >
                            {log.result}
                          </Badge>
                          {expandedLog === log.id ? (
                            <ChevronDown className="h-4 w-4 text-slate-400" />
                          ) : (
                            <ChevronRight className="h-4 w-4 text-slate-400" />
                          )}
                        </div>
                      </div>
                    </div>
                    {expandedLog === log.id && (
                      <div className="px-3 pb-3 pt-1 border-t border-slate-200 bg-slate-50">
                        <div className="grid grid-cols-3 gap-4 mt-2">
                          <div>
                            <p className="text-xs text-slate-500 mb-1">Audit ID</p>
                            <p className="text-xs font-mono font-semibold text-slate-900">{log.id}</p>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500 mb-1">Bias Score</p>
                            <div className="flex items-center gap-2">
                              <p className="text-xs font-semibold text-slate-900">{log.biasScore}/100</p>
                              <div className="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-green-500"
                                  style={{ width: `${log.biasScore}%` }}
                                />
                              </div>
                            </div>
                          </div>
                          <div>
                            <p className="text-xs text-slate-500 mb-1">Compliance Score</p>
                            <div className="flex items-center gap-2">
                              <p className="text-xs font-semibold text-slate-900">{log.complianceScore}/100</p>
                              <div className="flex-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-blue-500"
                                  style={{ width: `${log.complianceScore}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
