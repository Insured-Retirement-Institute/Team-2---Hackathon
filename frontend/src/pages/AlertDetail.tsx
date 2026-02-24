import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { BellOff, Clock, AlertTriangle, CheckCircle2, ChevronDown, FileText, ArrowLeft } from "lucide-react";
import { toast } from "sonner";

import { WorkflowStepper } from "@/components/modal/WorkflowStepper";
import type { WorkflowStep } from "@/components/modal/WorkflowStepper";
import { PolicySummary } from "@/components/modal/PolicySummary";
import { OverviewTab } from "@/components/modal/OverviewTab";
import { CompareTab } from "@/components/modal/CompareTab";
import { ActionTab } from "@/components/modal/ActionTab";

import type { AlertDetail, ComparisonParameters, SuitabilityData, ProductOption } from "@/types/alert-detail";
import { fetchAlertDetail, fetchClientProfile, saveClientProfile, runComparison, recompareWithProducts } from "@/api/alert-detail";
import type { ComparisonData } from "@/types/alert-detail";

export function AlertDetailPage() {
  const { alertId } = useParams<{ alertId: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<AlertDetail | null>(null);
  const [activeTab, setActiveTab] = useState<WorkflowStep>("overview");
  const [completedSteps, setCompletedSteps] = useState<Set<WorkflowStep>>(new Set());

  const [parameters, setParameters] = useState<ComparisonParameters | null>(null);
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);

  const [suitabilityData, setSuitabilityData] = useState<SuitabilityData | null>(null);
  const [disclosuresAcknowledged, setDisclosuresAcknowledged] = useState(false);
  const [transactionId, setTransactionId] = useState("");

  const [auditLogExpanded, setAuditLogExpanded] = useState(false);
  const [editingProfile, setEditingProfile] = useState(false);

  useEffect(() => {
    if (alertId) loadDetail();
  }, [alertId]);

  const loadDetail = async () => {
    setLoading(true);
    try {
      const [detailData, profileData] = await Promise.all([
        fetchAlertDetail(alertId!),
        fetchClientProfile(alertId!),
      ]);
      setDetail(detailData);
      setSuitabilityData(detailData.suitabilityData);
      setParameters(profileData.parameters);
    } catch {
      toast.error("Failed to load alert details");
    } finally {
      setLoading(false);
    }
  };

  const handleStepClick = (step: WorkflowStep) => {
    if (activeTab === "overview" && step !== "overview") {
      setCompletedSteps((prev) => new Set(prev).add("overview"));
    }
    if (step !== "compare") setEditingProfile(false);
    setActiveTab(step);
  };

  const handleRunComparison = async () => {
    setCompareLoading(true);
    try {
      if (parameters) await saveClientProfile(alertId!, parameters);
      const result = await runComparison(alertId!);
      setComparisonData(result.comparisonData);
      setCompletedSteps((prev) => new Set(prev).add("compare"));
    } catch {
      toast.error("Failed to run comparison");
    } finally {
      setCompareLoading(false);
    }
  };

  const handleTransactionConfirm = (_type: "renew" | "replace", _rationale: string, _clientStatement: string) => {
    const txId = `TXN-2026-${Math.floor(Math.random() * 10000)}`;
    setTransactionId(txId);
    setCompletedSteps((prev) => new Set(prev).add("action"));
    toast.success(`Transaction ${txId} submitted successfully`);
  };

  const handleRecompareWithProducts = async (products: ProductOption[]) => {
    setCompareLoading(true);
    try {
      const result = await recompareWithProducts(alertId!, products);
      setComparisonData(result.comparisonData);
    } catch {
      toast.error("Failed to update comparison");
    } finally {
      setCompareLoading(false);
    }
  };

  const goBack = () => navigate("/");

  if (loading || !detail) {
    return (
      <div className="h-screen flex items-center justify-center bg-slate-50">
        <div className="text-slate-600">Loading alert details...</div>
      </div>
    );
  }

  const { alert, clientAlerts, policyData, disclosureItems, transactionOptions, auditLog } = detail;

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      {/* Header */}
      <div className="h-20 px-8 flex items-center justify-between border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50 shrink-0">
        <div className="flex items-center gap-4 flex-1">
          <Button variant="ghost" size="sm" onClick={goBack} className="h-10 w-10 p-0">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h3 className="text-2xl font-bold text-slate-900 mb-1">
              {alert.alertType.includes("replacement") ? "Replacement Review" : "Renewal Review"}
            </h3>
            <div className="flex items-center gap-4">
              <span className="text-sm font-mono text-slate-700 bg-white px-3 py-1 rounded-md border border-slate-200">
                {alert.policyId}
              </span>
              <span className="text-sm font-semibold text-slate-700">{alert.clientName}</span>
              <div className="flex items-center gap-2 bg-red-100 px-3 py-1 rounded-md">
                <Clock className="h-4 w-4 text-red-700" />
                <span className="text-sm font-bold text-red-700">{alert.daysUntilRenewal} days until renewal</span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" className="h-10 px-4">
            <BellOff className="h-4 w-4 mr-2" /> Snooze
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Left: Policy Summary */}
        <div className="w-[400px] border-r border-slate-200 bg-slate-50 shrink-0 overflow-y-auto">
          <div className="p-6">
            <PolicySummary policy={policyData} />
          </div>
        </div>

        {/* Right: Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Banners */}
          <div className="px-8 pt-6 space-y-3">
            {policyData.isMinRateRenewal && (
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600 shrink-0" />
                <span className="text-sm text-red-800 font-medium">
                  CRITICAL: Policy renewing at guaranteed minimum rate ({alert.renewalRate}). Immediate action required.
                </span>
              </div>
            )}
            {alert.hasDataException && (
              <div className="flex items-center gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0" />
                <span className="text-sm text-amber-800 font-medium">
                  Data quality issues detected. Resolve before submission.
                </span>
              </div>
            )}
          </div>

          {/* Workflow Stepper + Tab Content */}
          <div className="mx-8 mt-6 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col flex-1 min-h-0">
            <WorkflowStepper currentStep={activeTab} completedSteps={completedSteps} onStepClick={handleStepClick} />
            <div className="flex-1 overflow-y-auto p-8">
              {activeTab === "overview" && (
                <OverviewTab alert={alert} clientAlerts={clientAlerts} features={policyData.features} onEditProfile={() => { setEditingProfile(true); setActiveTab("compare"); }} />
              )}
              {activeTab === "compare" && parameters && (
                <CompareTab
                  parameters={parameters}
                  comparisonData={comparisonData}
                  clientName={alert.clientName}
                  policyValue={alert.currentValue}
                  isLoading={compareLoading}
                  onParametersChange={setParameters}
                  onRunComparison={handleRunComparison}
                  onRecompareWithProducts={handleRecompareWithProducts}
                  onEditProfile={() => { setEditingProfile(true); setActiveTab("compare"); }}
                  startOnParameters={editingProfile}
                  key={editingProfile ? "edit" : "default"}
                />
              )}
              {activeTab === "action" && suitabilityData && (
                <ActionTab
                  clientName={alert.clientName}
                  suitabilityData={suitabilityData}
                  onSuitabilityChange={setSuitabilityData}
                  disclosureItems={disclosureItems}
                  disclosuresAcknowledged={disclosuresAcknowledged}
                  onDisclosuresComplete={setDisclosuresAcknowledged}
                  transactionOptions={transactionOptions}
                  onTransactionConfirm={handleTransactionConfirm}
                  transactionId={transactionId}
                />
              )}
            </div>
          </div>

          {/* Audit Log */}
          <div className="px-8 py-4 shrink-0">
            <button
              onClick={() => setAuditLogExpanded(!auditLogExpanded)}
              className="w-full flex items-center justify-between text-sm text-slate-600 hover:bg-slate-50 rounded-lg h-10 px-4"
            >
              <span className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span className="font-semibold">Activity Audit Log</span>
              </span>
              <ChevronDown className={`h-4 w-4 transition-transform ${auditLogExpanded ? "rotate-180" : ""}`} />
            </button>
            {auditLogExpanded && (
              <div className="mt-2 border border-slate-200 rounded-xl overflow-hidden bg-white">
                <div className="bg-slate-50 px-6 py-3 border-b border-slate-200">
                  <p className="text-xs text-slate-600">All actions logged for compliance (immutable record)</p>
                </div>
                <div className="divide-y divide-slate-100 max-h-48 overflow-y-auto">
                  {auditLog.map((log, idx) => (
                    <div key={idx} className="px-6 py-3 hover:bg-slate-50">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-slate-600 font-mono">{log.timestamp}</span>
                        <span className="text-slate-500">{log.user}</span>
                      </div>
                      <div className="text-sm">
                        <span className="font-semibold text-slate-900">{log.action}</span>
                        <span className="text-slate-600 ml-2">— {log.details}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="h-16 px-8 border-t border-slate-200 flex items-center justify-between bg-gradient-to-r from-slate-50 to-slate-100 shrink-0">
        <div className="flex items-center gap-3">
          {suitabilityData?.score === 100 && disclosuresAcknowledged ? (
            <>
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <span className="text-green-800 font-bold text-sm">Ready to proceed with transaction</span>
            </>
          ) : (
            <>
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              <span className="text-amber-800 font-semibold text-sm">Complete suitability and disclosures to continue</span>
            </>
          )}
        </div>
        <Button onClick={goBack} className="bg-blue-600 hover:bg-blue-700 h-10 px-6 font-semibold">
          Back to Dashboard
        </Button>
      </div>
    </div>
  );
}
