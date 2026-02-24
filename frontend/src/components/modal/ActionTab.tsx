import { useState } from "react";
import type { SuitabilityData, DisclosureItem, TransactionOption } from "@/types/alert-detail";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { CheckCircle2, AlertTriangle, FileText, ArrowRight } from "lucide-react";

interface ActionTabProps {
  clientName: string;
  suitabilityData: SuitabilityData;
  onSuitabilityChange: (data: SuitabilityData) => void;
  disclosureItems: DisclosureItem[];
  disclosuresAcknowledged: boolean;
  onDisclosuresComplete: (complete: boolean) => void;
  transactionOptions: TransactionOption[];
  onTransactionConfirm: (type: "renew" | "replace", rationale: string, clientStatement: string) => void;
  transactionId: string;
}

export function ActionTab({
  clientName: _clientName,
  suitabilityData,
  disclosureItems,
  disclosuresAcknowledged: _disclosuresAcknowledged,
  onDisclosuresComplete,
  transactionOptions,
  onTransactionConfirm,
  transactionId,
}: ActionTabProps) {
  const [acknowledgedIds, setAcknowledgedIds] = useState<Set<string>>(new Set());
  const [selectedTransaction, setSelectedTransaction] = useState<number | null>(null);
  const [rationale, setRationale] = useState("");
  const [clientStatement, setClientStatement] = useState("");

  const allDisclosuresAcked = disclosureItems.filter((d) => d.required).every((d) => acknowledgedIds.has(d.id));

  const toggleDisclosure = (id: string) => {
    const next = new Set(acknowledgedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setAcknowledgedIds(next);
    const allRequired = disclosureItems.filter((d) => d.required).every((d) => next.has(d.id));
    onDisclosuresComplete(allRequired);
  };

  const handleSubmit = () => {
    if (selectedTransaction === null) return;
    const opt = transactionOptions[selectedTransaction];
    onTransactionConfirm(opt.type, rationale, clientStatement);
  };

  return (
    <div className="space-y-8">
      {/* Step 1: Suitability Summary */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <span className="flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-xs font-bold">1</span>
          <h3 className="text-lg font-bold text-slate-900">Suitability Confirmation</h3>
          {suitabilityData.score === 100 && <CheckCircle2 className="h-5 w-5 text-green-500" />}
        </div>
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <SuitRow label="Objectives" value={suitabilityData.clientObjectives} />
            <SuitRow label="Risk Tolerance" value={suitabilityData.riskTolerance} />
            <SuitRow label="Time Horizon" value={suitabilityData.timeHorizon} />
            <SuitRow label="Liquidity Needs" value={suitabilityData.liquidityNeeds} />
            <SuitRow label="Guaranteed Income" value={suitabilityData.guaranteedIncome} />
            <SuitRow label="Advisor Eligibility" value={suitabilityData.advisorEligibility} />
          </div>
          <div className="mt-4 flex items-center gap-2">
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-300">
              Score: {suitabilityData.score}/100
            </Badge>
            {suitabilityData.isPrefilled && (
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300">Pre-filled</Badge>
            )}
          </div>
        </div>
      </div>

      <Separator />

      {/* Step 2: Disclosures */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <span className="flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-xs font-bold">2</span>
          <h3 className="text-lg font-bold text-slate-900">Disclosure Checklist</h3>
          {allDisclosuresAcked && <CheckCircle2 className="h-5 w-5 text-green-500" />}
        </div>
        <div className="space-y-2">
          {disclosureItems.map((item) => (
            <label
              key={item.id}
              className="flex items-start gap-3 p-4 bg-white border border-slate-200 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors"
            >
              <input
                type="checkbox"
                checked={acknowledgedIds.has(item.id)}
                onChange={() => toggleDisclosure(item.id)}
                className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <div className="text-sm font-medium text-slate-900">{item.title || item.label}</div>
                {item.description && <div className="text-xs text-slate-500 mt-0.5">{item.description}</div>}
                {item.documentName && (
                  <div className="flex items-center gap-1 mt-1 text-xs text-blue-600">
                    <FileText className="h-3 w-3" /> {item.documentName}
                  </div>
                )}
              </div>
            </label>
          ))}
        </div>
      </div>

      <Separator />

      {/* Step 3: Transaction Selection */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <span className="flex items-center justify-center h-6 w-6 rounded-full bg-blue-600 text-white text-xs font-bold">3</span>
          <h3 className="text-lg font-bold text-slate-900">Transaction Selection</h3>
        </div>

        {!allDisclosuresAcked && (
          <div className="flex items-center gap-2 p-4 bg-amber-50 border border-amber-200 rounded-lg mb-4">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <span className="text-sm text-amber-800">Complete all disclosures above to proceed with transaction.</span>
          </div>
        )}

        <div className="space-y-3">
          {transactionOptions.map((opt, idx) => (
            <div
              key={idx}
              onClick={() => allDisclosuresAcked && opt.isAvailable && setSelectedTransaction(idx)}
              className={`p-5 border-2 rounded-xl cursor-pointer transition-all ${
                selectedTransaction === idx
                  ? "border-blue-500 bg-blue-50"
                  : opt.isAvailable && allDisclosuresAcked
                    ? "border-slate-200 hover:border-blue-300"
                    : "border-slate-200 opacity-50 cursor-not-allowed"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={opt.type === "replace" ? "bg-blue-50 text-blue-700 border-blue-300" : "bg-slate-100 text-slate-700 border-slate-300"}>
                    {opt.type === "replace" ? "Replace" : "Renew"}
                  </Badge>
                  {!opt.isAvailable && <Badge variant="outline" className="bg-red-50 text-red-700 border-red-300">Unavailable</Badge>}
                </div>
              </div>
              <div className="text-sm font-medium text-slate-900">{opt.label}</div>
              {opt.pros && opt.pros.length > 0 && (
                <div className="mt-2 space-y-1">
                  {opt.pros.map((p, i) => (
                    <div key={i} className="text-xs text-green-700 flex items-start gap-1">
                      <span>+</span> {p}
                    </div>
                  ))}
                </div>
              )}
              {opt.cons && opt.cons.length > 0 && (
                <div className="mt-1 space-y-1">
                  {opt.cons.map((c, i) => (
                    <div key={i} className="text-xs text-red-600 flex items-start gap-1">
                      <span>−</span> {c}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Rationale & Submit */}
        {selectedTransaction !== null && (
          <div className="mt-6 space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700 block mb-1">Advisor Rationale</label>
              <textarea
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                placeholder="Explain why this transaction is in the client's best interest..."
                className="w-full h-20 rounded-lg border border-slate-200 p-3 text-sm resize-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700 block mb-1">Client Statement</label>
              <textarea
                value={clientStatement}
                onChange={(e) => setClientStatement(e.target.value)}
                placeholder="Client's acknowledgment statement..."
                className="w-full h-20 rounded-lg border border-slate-200 p-3 text-sm resize-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
              />
            </div>
            <Button
              onClick={handleSubmit}
              disabled={!rationale || !clientStatement}
              className="w-full h-12 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold"
            >
              <ArrowRight className="h-5 w-5 mr-2" />
              Submit Transaction
            </Button>
          </div>
        )}

        {/* Transaction Confirmation */}
        {transactionId && (
          <div className="mt-6 p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
            <div className="flex items-center gap-4">
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle2 className="h-7 w-7 text-green-600" />
              </div>
              <div>
                <div className="text-lg font-bold text-green-900">Transaction Created</div>
                <div className="text-sm text-green-700 mt-1">
                  Transaction ID: <span className="font-mono font-bold">{transactionId}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function SuitRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-sm font-medium text-slate-900 truncate">{value}</div>
    </div>
  );
}
