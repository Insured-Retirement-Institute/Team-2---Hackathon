import type { PolicyData } from "@/types/alert-detail";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

interface PolicySummaryProps {
  policy: PolicyData;
}

export function PolicySummary({ policy }: PolicySummaryProps) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-bold text-slate-900 mb-1">Policy Summary</h3>
        <p className="text-xs text-slate-500 font-mono">{policy.contractId}</p>
      </div>

      <div className="space-y-3">
        <Row label="Client" value={policy.clientName} />
        <Row label="Carrier" value={policy.carrier} />
        <Row label="Product" value={policy.productName} />
        <Row label="Issue Date" value={policy.issueDate} />
        <Separator />
        <Row label="Current Value" value={policy.currentValue} bold />
        <Row label="Surrender Value" value={policy.surrenderValue} />
        <Separator />
        <Row label="Current Rate" value={policy.currentRate} bold />
        <Row label="Renewal Rate" value={policy.renewalRate} highlight={policy.isMinRateRenewal ? "red" : undefined} bold />
        <Row label="Guaranteed Min" value={policy.guaranteedMinRate} />
        <Row label="Renewal Date" value={policy.renewalDate} />
        <Separator />
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-500">Suitability</span>
          <Badge
            variant="outline"
            className={
              policy.suitabilityStatus === "complete"
                ? "bg-green-50 text-green-700 border-green-300"
                : policy.suitabilityStatus === "incomplete"
                  ? "bg-amber-50 text-amber-700 border-amber-300"
                  : "bg-slate-50 text-slate-700 border-slate-300"
            }
          >
            {policy.suitabilityStatus}
          </Badge>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-500">Eligibility</span>
          <Badge
            variant="outline"
            className={
              policy.eligibilityStatus === "eligible"
                ? "bg-green-50 text-green-700 border-green-300"
                : "bg-red-50 text-red-700 border-red-300"
            }
          >
            {policy.eligibilityStatus}
          </Badge>
        </div>
      </div>

      {/* Key policy metrics */}
      {(policy.features.surrenderCharge || policy.features.withdrawalAllowance) && (
        <>
          <Separator />
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-slate-700">Key Metrics</h4>
            {policy.features.surrenderCharge && <Row label="Surrender Charge" value={policy.features.surrenderCharge} />}
            {policy.features.withdrawalAllowance && <Row label="Free Withdrawal" value={policy.features.withdrawalAllowance} />}
            {policy.features.mvaPenalty && <Row label="MVA Penalty" value={policy.features.mvaPenalty} highlight="red" />}
            {policy.features.rateGuarantee && <Row label="Rate Guarantee" value={policy.features.rateGuarantee} />}
          </div>
        </>
      )}
    </div>
  );
}

function Row({ label, value, bold, highlight }: { label: string; value: string; bold?: boolean; highlight?: "red" }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-slate-500">{label}</span>
      <span
        className={`text-sm ${bold ? "font-bold" : "font-medium"} ${highlight === "red" ? "text-red-700" : "text-slate-900"}`}
      >
        {value}
      </span>
    </div>
  );
}
