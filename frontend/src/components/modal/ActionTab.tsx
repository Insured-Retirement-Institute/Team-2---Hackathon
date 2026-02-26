import { useState } from "react";
import type {
  SuitabilityData,
  DisclosureItem,
  TransactionOption,
} from "@/types/alert-detail";
import { generateAISummary } from "@/api/suitability";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import {
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  AlertCircle,
  Info,
  FileDown,
  ArrowRight,
  Lock,
  User,
  DollarSign,
  FileText,
  Calendar,
} from "lucide-react";

interface ActionTabProps {
  clientName: string;
  suitabilityData: SuitabilityData;
  onSuitabilityChange: (data: SuitabilityData) => void;
  disclosureItems: DisclosureItem[];
  disclosuresAcknowledged: boolean;
  onDisclosuresComplete: (complete: boolean) => void;
  transactionOptions: TransactionOption[];
  onTransactionConfirm: (
    type: "renew" | "replace",
    rationale: string,
    clientStatement: string,
  ) => void;
  transactionId: string;
}

type StepId = "suitability" | "transaction" | "disclosures" | "documentation";

interface StepConfig {
  id: StepId;
  title: string;
  subtitle: string;
  icon: React.ComponentType<{ className?: string }>;
}

const STEPS: StepConfig[] = [
  {
    id: "suitability",
    title: "Suitability Analysis",
    subtitle: "Verify client profile & product alignment",
    icon: User,
  },
  {
    id: "transaction",
    title: "Transaction Details",
    subtitle: "Select transaction type",
    icon: DollarSign,
  },
  {
    id: "disclosures",
    title: "Disclosure Review",
    subtitle: "Client acknowledgements & agreements",
    icon: FileText,
  },
  {
    id: "documentation",
    title: "Documentation",
    subtitle: "Auto-generated summary",
    icon: Calendar,
  },
];

export function ActionTab({
  suitabilityData,
  onSuitabilityChange,
  disclosureItems,
  onDisclosuresComplete,
  transactionOptions,
  onTransactionConfirm,
  transactionId,
}: ActionTabProps) {
  const [expandedStep, setExpandedStep] = useState<StepId | null>(null);
  const [completedSteps, setCompletedSteps] = useState<Set<StepId>>(new Set(["suitability"]));
  const [suitabilityEdited, setSuitabilityEdited] = useState(false);
  const [acknowledgedIds, setAcknowledgedIds] = useState<Set<string>>(
    new Set(),
  );
  const [selectedTransaction, setSelectedTransaction] = useState<number | null>(
    null,
  );
  const [aiSummary, setAiSummary] = useState<string>("");

  // Fetch AI summary when suitability data changes
  useEffect(() => {
    if (suitabilityData && transactionId) {
      generateAISummary(transactionId, suitabilityData)
        .then(setAiSummary)
        .catch((err) => {
          console.error("Failed to generate AI summary:", err);
          setAiSummary("Unable to generate summary at this time.");
        });
    }
  }, [suitabilityData, transactionId]);

  const updateField = (
    field: keyof SuitabilityData,
    value: string | string[],
  ) => {
    onSuitabilityChange({ ...suitabilityData, [field]: value });
    setSuitabilityEdited(true);
    setCompletedSteps((prev) => {
      const next = new Set(prev);
      next.delete("suitability");
      return next;
    });
  };

  const toggleStep = (stepId: StepId) => {
    setExpandedStep(expandedStep === stepId ? null : stepId);
  };

  const markStepComplete = (stepId: StepId) => {
    setCompletedSteps((prev) => new Set([...prev, stepId]));
    if (stepId === "suitability") {
      setSuitabilityEdited(false);
    }
    const currentIndex = STEPS.findIndex((s) => s.id === stepId);
    if (currentIndex < STEPS.length - 1) {
      setExpandedStep(STEPS[currentIndex + 1].id);
    }
  };

  const toggleDisclosure = (id: string) => {
    const next = new Set(acknowledgedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setAcknowledgedIds(next);
    const allRequired = disclosureItems
      .filter((d) => d.required)
      .every((d) => next.has(d.id));
    onDisclosuresComplete(allRequired);
  };

  const allRequiredAcknowledged = disclosureItems
    .filter((d) => d.required)
    .every((d) => acknowledgedIds.has(d.id));

  const handleFinalSubmit = () => {
    if (selectedTransaction === null) return;
    const opt = transactionOptions[selectedTransaction];
    onTransactionConfirm(opt.type, aiSummary, "");
  };

  const handleExportPDF = () => {
    toast.warning("PDF export coming soon", {
      description: "This feature is currently under development.",
    });
  };

  const isAllComplete = completedSteps.size === STEPS.length;

  return (
    <div className="space-y-6">
      {/* Progress Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="font-bold text-slate-900 text-base">
              Action Workflow Progress
            </div>
            <div className="text-sm text-slate-600 mt-0.5">
              {completedSteps.size} of {STEPS.length} steps complete
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-900">
              {Math.round((completedSteps.size / STEPS.length) * 100)}%
            </div>
            <div className="text-xs text-slate-600">Complete</div>
          </div>
        </div>
        <div className="h-2 bg-blue-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 transition-all duration-500"
            style={{ width: `${(completedSteps.size / STEPS.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Step Accordions */}
      <div className="space-y-3">
        {STEPS.map((step, index) => {
          const Icon = step.icon;
          const isComplete = completedSteps.has(step.id);
          const isExpanded = expandedStep === step.id;
          const canExpand = index === 0 || completedSteps.has(STEPS[index - 1].id);

          return (
            <div
              key={step.id}
              className={`border-2 rounded-xl overflow-hidden transition-all ${
                isComplete
                  ? "border-green-300 bg-green-50"
                  : isExpanded
                    ? "border-blue-400 bg-blue-50 shadow-lg"
                    : "border-slate-200 bg-white"
              }`}
            >
              {/* Step Header */}
              <button
                onClick={() => canExpand && toggleStep(step.id)}
                disabled={!canExpand}
                className={`w-full p-4 flex items-center justify-between transition-all ${
                  canExpand
                    ? "cursor-pointer hover:bg-slate-50"
                    : "cursor-not-allowed opacity-60"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      isComplete
                        ? "bg-green-600"
                        : isExpanded
                          ? "bg-blue-600"
                          : "bg-slate-200"
                    }`}
                  >
                    {isComplete ? (
                      <CheckCircle2 className="h-5 w-5 text-white" />
                    ) : (
                      <Icon
                        className={`h-5 w-5 ${
                          isExpanded ? "text-white" : "text-slate-600"
                        }`}
                      />
                    )}
                  </div>
                  <div className="text-left">
                    <div className="font-bold text-slate-900">{step.title}</div>
                    <div className="text-sm text-slate-600">{step.subtitle}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {isComplete && (
                    <Badge
                      variant="secondary"
                      className="bg-green-100 text-green-800 border-green-300"
                    >
                      Complete
                    </Badge>
                  )}
                  <ChevronDown
                    className={`h-5 w-5 text-slate-400 transition-transform ${
                      isExpanded ? "rotate-180" : ""
                    }`}
                  />
                </div>
              </button>

              {/* Step Content */}
              {isExpanded && (
                <div className="border-t border-slate-200 p-5 bg-white">
                  {step.id === "suitability" && (
                    <div className="space-y-6">
                      {/* Client Objectives */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                          Client Objectives
                        </label>
                        <textarea
                          value={suitabilityData.clientObjectives}
                          onChange={(e) => updateField("clientObjectives", e.target.value)}
                          className="w-full h-20 rounded-lg border border-slate-300 p-3 text-sm resize-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                          placeholder="Describe the client's primary financial objectives..."
                        />
                      </div>

                      {/* Risk Tolerance */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                          Risk Tolerance
                        </label>
                        <div className="grid grid-cols-3 gap-3">
                          {[
                            { value: "conservative", label: "Conservative", desc: "Prioritize safety & guarantees" },
                            { value: "moderate", label: "Moderate", desc: "Balance growth & protection" },
                            { value: "aggressive", label: "Aggressive", desc: "Focus on growth potential" },
                          ].map((risk) => {
                            const isSelected = suitabilityData.riskTolerance.toLowerCase() === risk.value;
                            return (
                              <button
                                key={risk.value}
                                onClick={() => updateField("riskTolerance", risk.value)}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                  isSelected
                                    ? "border-blue-500 bg-blue-50"
                                    : "border-slate-200 bg-white hover:border-slate-300"
                                }`}
                              >
                                <div className="text-sm font-semibold text-slate-900">{risk.label}</div>
                                <div className="text-xs text-slate-600 mt-1">{risk.desc}</div>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Time Horizon */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                          Time Horizon
                        </label>
                        <div className="grid grid-cols-3 gap-3">
                          {[
                            { value: "short", label: "Short", desc: "< 5 years" },
                            { value: "medium", label: "Medium", desc: "5-10 years" },
                            { value: "long", label: "Long", desc: "10+ years" },
                          ].map((horizon) => {
                            const isSelected = suitabilityData.timeHorizon.toLowerCase().includes(horizon.value);
                            return (
                              <button
                                key={horizon.value}
                                onClick={() => updateField("timeHorizon", horizon.value)}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                  isSelected
                                    ? "border-blue-500 bg-blue-50"
                                    : "border-slate-200 bg-white hover:border-slate-300"
                                }`}
                              >
                                <div className="text-sm font-semibold text-slate-900">{horizon.label}</div>
                                <div className="text-xs text-slate-600 mt-1">{horizon.desc}</div>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Liquidity Needs */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-3">
                          Liquidity Needs
                        </label>
                        <div className="space-y-4">
                          <input
                            type="range"
                            min="1"
                            max="5"
                            value={
                              suitabilityData.liquidityNeeds.includes("Minimal") ? 1 :
                              suitabilityData.liquidityNeeds.includes("Low") ? 2 :
                              suitabilityData.liquidityNeeds.includes("Moderate") ? 3 :
                              suitabilityData.liquidityNeeds.includes("High") && !suitabilityData.liquidityNeeds.includes("Very") ? 4 : 5
                            }
                            onChange={(e) => {
                              const level = parseInt(e.target.value);
                              const labels = ["Minimal", "Low", "Moderate", "High", "Very High"];
                              updateField("liquidityNeeds", labels[level - 1]);
                            }}
                            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                          />
                          <div className="flex justify-between text-xs">
                            {[
                              { label: "Minimal", desc: "Rarely need access" },
                              { label: "Low", desc: "Occasional access" },
                              { label: "Moderate", desc: "10-15% annually" },
                              { label: "High", desc: "15-20% annually" },
                              { label: "Very High", desc: "20%+ annually" },
                            ].map((liquidity, idx) => {
                              const isSelected = suitabilityData.liquidityNeeds.includes(liquidity.label);
                              return (
                                <div key={liquidity.label} className={`text-center ${idx === 0 ? 'text-left' : idx === 4 ? 'text-right' : ''}`}>
                                  <div className={`font-semibold ${isSelected ? 'text-blue-600' : 'text-slate-600'}`}>
                                    {liquidity.label}
                                  </div>
                                  <div className="text-slate-500 text-[10px]">{liquidity.desc}</div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>

                      {/* Guaranteed Income Priority */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                          Guaranteed Income Priority
                        </label>
                        <div className="grid grid-cols-3 gap-3">
                          {[
                            { value: "not-required", label: "Not Required", desc: "Accumulation focus" },
                            { value: "preferred", label: "Preferred", desc: "Desired but flexible" },
                            { value: "required", label: "Required", desc: "Essential to strategy" },
                          ].map((income) => {
                            const isSelected = suitabilityData.guaranteedIncome.toLowerCase().includes(income.value);
                            return (
                              <button
                                key={income.value}
                                onClick={() => updateField("guaranteedIncome", income.value)}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                  isSelected
                                    ? "border-blue-500 bg-blue-50"
                                    : "border-slate-200 bg-white hover:border-slate-300"
                                }`}
                              >
                                <div className="text-sm font-semibold text-slate-900">{income.label}</div>
                                <div className="text-xs text-slate-600 mt-1">{income.desc}</div>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Rate Expectations */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                          Rate Expectations
                        </label>
                        <div className="grid grid-cols-3 gap-3">
                          {[
                            { value: "Market Average", desc: "Competitive baseline rates" },
                            { value: "Above Average", desc: "Better than market rates" },
                            { value: "Premium Rates", desc: "Top-tier rate expectations" },
                          ].map((rate) => {
                            const isSelected = suitabilityData.rateExpectations.includes(rate.value);
                            return (
                              <button
                                key={rate.value}
                                onClick={() => updateField("rateExpectations", rate.value)}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                  isSelected
                                    ? "border-blue-500 bg-blue-50"
                                    : "border-slate-200 bg-white hover:border-slate-300"
                                }`}
                              >
                                <div className="text-sm font-semibold text-slate-900">{rate.value}</div>
                                <div className="text-xs text-slate-600 mt-1">{rate.desc}</div>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Surrender Timeline */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                          Surrender Timeline
                        </label>
                        <div className="grid grid-cols-4 gap-3">
                          {[
                            { value: "3-5", label: "3-5 Years", desc: "Short surrender period" },
                            { value: "6-8", label: "6-8 Years", desc: "Medium surrender period" },
                            { value: "9-10", label: "9-10 Years", desc: "Standard surrender period" },
                            { value: "10-plus", label: "10+ Years", desc: "Extended surrender period" },
                          ].map((timeline) => {
                            const isSelected = suitabilityData.surrenderTimeline.includes(timeline.value);
                            return (
                              <button
                                key={timeline.value}
                                onClick={() => updateField("surrenderTimeline", timeline.value)}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                  isSelected
                                    ? "border-blue-500 bg-blue-50"
                                    : "border-slate-200 bg-white hover:border-slate-300"
                                }`}
                              >
                                <div className="text-sm font-semibold text-slate-900">{timeline.label}</div>
                                <div className="text-xs text-slate-600 mt-1">{timeline.desc}</div>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Tax Considerations */}
                      <div>
                        <label className="text-sm font-medium text-slate-700 block mb-2">
                          Tax Considerations
                        </label>
                        <textarea
                          value={suitabilityData.taxConsiderations}
                          onChange={(e) => updateField("taxConsiderations", e.target.value)}
                          className="w-full h-16 rounded-lg border border-slate-300 p-3 text-sm resize-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                          placeholder="Tax bracket, deferred growth needs, etc."
                        />
                      </div>

                      {/* Score Badge */}
                      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-5 w-5 text-green-600" />
                          <span className="text-sm font-medium text-green-900">
                            Suitability Score
                          </span>
                        </div>
                        <Badge className="bg-green-600 text-white text-base px-3 py-1">
                          {suitabilityData.score}/100
                        </Badge>
                      </div>

                      <Button
                        onClick={() => markStepComplete("suitability")}
                        disabled={isComplete && !suitabilityEdited}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium"
                      >
                        {isComplete && !suitabilityEdited ? (
                          <>
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Suitability Confirmed
                          </>
                        ) : (
                          <>
                            Confirm Suitability Analysis
                            <ChevronRight className="h-4 w-4 ml-2" />
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  {step.id === "transaction" && (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        {transactionOptions.map((opt, idx) => {
                          const isSelected = selectedTransaction === idx;
                          return (
                            <button
                              key={idx}
                              onClick={() => setSelectedTransaction(idx)}
                              disabled={!opt.isAvailable}
                              className={`p-6 rounded-lg border-2 transition-all text-left ${
                                !opt.isAvailable
                                  ? "opacity-50 cursor-not-allowed bg-slate-50"
                                  : isSelected
                                  ? "border-blue-500 bg-blue-50 shadow-lg"
                                  : "border-slate-200 bg-white hover:border-slate-300"
                              }`}
                            >
                              <div className="flex items-center justify-between mb-3">
                                <Badge
                                  className={
                                    opt.type === "replace"
                                      ? "bg-blue-100 text-blue-700 border-blue-300"
                                      : "bg-slate-100 text-slate-700 border-slate-300"
                                  }
                                >
                                  {opt.type === "replace" ? "Replacement" : "Renewal"}
                                </Badge>
                                <div
                                  className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                                    isSelected
                                      ? "border-blue-600 bg-blue-600"
                                      : "border-slate-300 bg-white"
                                  }`}
                                >
                                  {isSelected && (
                                    <div className="w-2.5 h-2.5 rounded-full bg-white" />
                                  )}
                                </div>
                              </div>
                              <div className="text-lg font-bold text-slate-900 mb-2">
                                {opt.label}
                              </div>
                              <p className="text-sm text-slate-600 mb-3">
                                {opt.description}
                              </p>
                              {opt.pros && opt.pros.length > 0 && (
                                <div className="space-y-1.5 mb-3">
                                  {opt.pros.map((pro, i) => (
                                    <div key={i} className="text-xs text-green-700 flex items-start gap-1">
                                      <span className="font-bold">+</span> {pro}
                                    </div>
                                  ))}
                                </div>
                              )}
                              {opt.requirements && opt.requirements.length > 0 && (
                                <div className="pt-3 border-t border-slate-200 text-xs text-slate-600">
                                  {opt.requirements.join(" • ")}
                                </div>
                              )}
                              {!opt.isAvailable && opt.unavailableReason && (
                                <div className="pt-3 border-t border-red-200 text-xs text-red-600 flex items-start gap-1">
                                  <AlertCircle className="h-3 w-3 mt-0.5" />
                                  {opt.unavailableReason}
                                </div>
                              )}
                            </button>
                          );
                        })}
                      </div>

                      <Button
                        onClick={() => markStepComplete("transaction")}
                        disabled={isComplete || selectedTransaction === null}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium"
                      >
                        {isComplete ? (
                          <>
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Transaction Confirmed
                          </>
                        ) : (
                          <>
                            Confirm Transaction Selection
                            <ChevronRight className="h-4 w-4 ml-2" />
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  {step.id === "disclosures" && (
                    <div className="space-y-4">
                      <div className="space-y-3">
                        {disclosureItems.map((item) => {
                          const isAcknowledged = acknowledgedIds.has(item.id);
                          return (
                            <label
                              key={item.id}
                              className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                                isAcknowledged
                                  ? "border-green-300 bg-green-50"
                                  : "border-slate-200 bg-white hover:bg-slate-50"
                              }`}
                            >
                              <input
                                type="checkbox"
                                checked={isAcknowledged}
                                onChange={() => toggleDisclosure(item.id)}
                                className="mt-1 h-5 w-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                              />
                              <div>
                                <div className="font-bold text-slate-900">
                                  {item.title || item.label}
                                </div>
                                {item.description && (
                                  <div className="text-sm text-slate-600 mt-1">
                                    {item.description}
                                  </div>
                                )}
                              </div>
                            </label>
                          );
                        })}
                      </div>
                      <Button
                        onClick={() => markStepComplete("disclosures")}
                        disabled={isComplete || !allRequiredAcknowledged}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium"
                      >
                        {isComplete ? (
                          <>
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Disclosures Acknowledged
                          </>
                        ) : (
                          <>
                            Confirm All Required Disclosures
                            <ChevronRight className="h-4 w-4 ml-2" />
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  {step.id === "documentation" && (
                    <div className="space-y-4">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-sm font-bold text-slate-900">
                            Summary
                          </label>
                          <div
                            className="flex items-center gap-1 text-xs text-slate-500 cursor-help"
                            title="This summary is automatically generated based on your suitability analysis and cannot be edited"
                          >
                            <Info className="h-3.5 w-3.5" />
                            <span>AI-generated</span>
                          </div>
                        </div>
                        <div className="bg-slate-50 border-2 border-slate-200 rounded-lg p-4">
                          <p className="text-sm text-slate-700 leading-relaxed">
                            {aiSummary}
                          </p>
                        </div>
                      </div>
                      <Button
                        onClick={() => markStepComplete("documentation")}
                        disabled={isComplete}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium"
                      >
                        {isComplete ? (
                          <>
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Documentation Complete
                          </>
                        ) : (
                          <>
                            Confirm Documentation
                            <ChevronRight className="h-4 w-4 ml-2" />
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Final Action Buttons */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-300 rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isAllComplete ? (
              <>
                <div className="h-12 w-12 rounded-full bg-green-500 flex items-center justify-center">
                  <CheckCircle2 className="h-7 w-7 text-white" />
                </div>
                <div>
                  <div className="font-bold text-green-900 text-lg">
                    All Steps Complete
                  </div>
                  <div className="text-sm text-green-700">
                    Ready to start application
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="h-12 w-12 rounded-full bg-amber-100 flex items-center justify-center">
                  <AlertCircle className="h-7 w-7 text-amber-600" />
                </div>
                <div>
                  <div className="font-bold text-amber-900 text-lg">
                    {STEPS.length - completedSteps.size} Step
                    {STEPS.length - completedSteps.size !== 1 ? "s" : ""}{" "}
                    Remaining
                  </div>
                  <div className="text-sm text-amber-700">
                    Complete all steps to enable submission
                  </div>
                </div>
              </>
            )}
          </div>
          <div className="flex gap-3">
            <Button
              onClick={handleExportPDF}
              variant="outline"
              className="border-slate-300 hover:bg-slate-50 text-slate-700 font-medium px-6"
            >
              <FileDown className="h-5 w-5 mr-2" />
              Export to PDF
            </Button>
            <Button
              onClick={handleFinalSubmit}
              disabled={!isAllComplete}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-slate-300 disabled:to-slate-400 text-white font-bold px-8"
            >
              {isAllComplete ? (
                <>
                  Start Application
                  <ArrowRight className="h-5 w-5 ml-2" />
                </>
              ) : (
                <>
                  <Lock className="h-5 w-5 mr-2" />
                  Complete Steps to Continue
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Transaction Confirmation */}
      {transactionId && (
        <div className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
              <CheckCircle2 className="h-7 w-7 text-green-600" />
            </div>
            <div>
              <div className="text-lg font-bold text-green-900">
                Transaction Created
              </div>
              <div className="text-sm text-green-700 mt-1">
                Transaction ID:{" "}
                <span className="font-mono font-bold">{transactionId}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
