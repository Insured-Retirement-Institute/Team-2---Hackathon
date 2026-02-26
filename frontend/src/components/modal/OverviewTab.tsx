import type { RenewalAlert } from "@/types/alerts";
import type { PolicyFeaturesData } from "@/types/alert-detail";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  TrendingDown,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  XCircle,
  FileText,
  Shield,
  Star,
  Lock,
  User,
  Pencil,
  Info,
  DollarSign,
} from "lucide-react";

interface OverviewTabProps {
  alert: RenewalAlert;
  clientAlerts: RenewalAlert[];
  features: PolicyFeaturesData;
  onEditProfile?: () => void;
  onNext?: () => void;
}

export function OverviewTab({
  alert,
  clientAlerts,
  features,
  onEditProfile,
  onNext,
}: OverviewTabProps) {
  const rateDrop = (
    ((parseFloat(alert.currentRate) - parseFloat(alert.renewalRate)) /
      parseFloat(alert.currentRate)) *
    100
  ).toFixed(0);

  return (
    <div className="space-y-6">
      {/* Client Profile Banner */}
      {onEditProfile && (
        <div className="flex items-center justify-between p-4 bg-indigo-50 border border-indigo-200 rounded-xl">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-indigo-100 flex items-center justify-center">
              <User className="h-5 w-5 text-indigo-600" />
            </div>
            <p className="text-sm text-slate-700">
              Product searches and filtering are based on the current client
              profile data on record.
            </p>
          </div>
          <button
            onClick={onEditProfile}
            className="flex items-center gap-1.5 text-sm font-semibold text-indigo-700 hover:text-indigo-900 hover:underline shrink-0"
          >
            <Pencil className="h-3.5 w-3.5" /> Edit Client Profile
          </button>
        </div>
      )}

      {/* Renewal Situation */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center shrink-0">
            <TrendingDown className="h-6 w-6 text-red-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-slate-900 mb-2">
              Renewal Situation
            </h3>
            <p className="text-sm text-slate-700 leading-relaxed">
              {alert.clientName}'s policy{" "}
              <span className="font-mono font-bold">{alert.policyId}</span> with{" "}
              {alert.carrier} is renewing in{" "}
              <span className="font-bold text-red-700">
                {alert.daysUntilRenewal} days
              </span>
              . The rate will drop from {alert.currentRate} to{" "}
              {alert.renewalRate} — a{" "}
              <span className="font-bold text-red-700">
                {rateDrop}% decrease
              </span>
              .{alert.isMinRate && " This is the guaranteed minimum rate."}
            </p>
            {/* Key metrics row */}
            <div className="flex gap-6 mt-4">
              <div className="bg-white rounded-lg px-4 py-2 border border-red-200">
                <div className="text-xs text-slate-500">Current Rate</div>
                <div className="text-lg font-bold text-slate-900">
                  {alert.currentRate}
                </div>
              </div>
              <div className="bg-white rounded-lg px-4 py-2 border border-red-200">
                <div className="text-xs text-slate-500">Renewal Rate</div>
                <div className="text-lg font-bold text-red-700">
                  {alert.renewalRate}
                </div>
              </div>
              <div className="bg-white rounded-lg px-4 py-2 border border-red-200">
                <div className="text-xs text-slate-500">Rate Drop</div>
                <div className="text-lg font-bold text-red-700">
                  {rateDrop}%
                </div>
              </div>
              <div className="bg-white rounded-lg px-4 py-2 border border-red-200">
                <div className="text-xs text-slate-500">Contract Value</div>
                <div className="text-lg font-bold text-slate-900">
                  {alert.currentValue}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Active Alerts */}
      <div>
        <h4 className="text-sm font-bold text-slate-900 mb-1 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-slate-600" />
          Active Alerts for This Client
        </h4>
        <p className="text-xs text-slate-600 mb-4">
          {clientAlerts.length}{" "}
          {clientAlerts.length === 1 ? "alert has" : "alerts have"} been
          generated based on policy data and client profile
        </p>
        <div className="space-y-3">
          {clientAlerts.map((a) => {
            const badge = getAlertBadge(a.alertType);
            const Icon = badge.icon;
            const evidence = getAlertEvidence(a);
            return (
              <div
                key={a.id}
                className="p-4 bg-slate-50 rounded-lg border border-slate-200"
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`h-9 w-9 rounded-lg flex items-center justify-center shrink-0 ${badge.bg}`}
                  >
                    <Icon className={`h-4 w-4 ${badge.text}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge
                        variant="outline"
                        className={`${badge.badge} text-xs px-2 py-0.5`}
                      >
                        {badge.label}
                      </Badge>
                      {a.priority === "high" && (
                        <Badge
                          variant="outline"
                          className="bg-red-100 text-red-700 border-red-300 text-xs px-2 py-0.5"
                        >
                          High Priority
                        </Badge>
                      )}
                    </div>
                    <h5 className="font-semibold text-slate-900 text-sm mb-1.5">
                      {a.alertDescription}
                    </h5>
                    {evidence.length > 0 && (
                      <ul className="space-y-1">
                        {evidence.map((item, idx) => (
                          <li
                            key={idx}
                            className="text-xs text-slate-600 flex items-start gap-2"
                          >
                            <span className="text-slate-400 mt-0.5">•</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <Separator />

      {/* Policy Features */}
      {features && (
        <div>
          <h4 className="font-bold text-slate-900 mb-4">
            Complete Policy Details
          </h4>
          <div className="grid grid-cols-2 gap-4">
            {features.features && (
              <FeatureSection
                title="Features"
                icon={Star}
                items={features.features}
                color="blue"
              />
            )}
            {features.benefits && (
              <FeatureSection
                title="Benefits"
                icon={Shield}
                items={features.benefits}
                color="green"
              />
            )}
            {features.riders && (
              <FeatureSection
                title="Riders"
                icon={FileText}
                items={features.riders}
                color="purple"
              />
            )}
            {features.limitations && (
              <FeatureSection
                title="Limitations"
                icon={Lock}
                items={features.limitations}
                color="amber"
              />
            )}
          </div>
        </div>
      )}

      {/* Next Button */}
      {onNext && (
        <div className="flex justify-end pt-4">
          <button
            onClick={onNext}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            Continue to Compare →
          </button>
        </div>
      )}
    </div>
  );
}

/* ── Alert badge + evidence helpers ───────────────────────── */
type AlertType = RenewalAlert["alertType"];

function getAlertBadge(type: AlertType) {
  const map: Record<
    AlertType,
    {
      label: string;
      badge: string;
      bg: string;
      text: string;
      icon: typeof AlertCircle;
    }
  > = {
    replacement_recommended: {
      label: "Replacement",
      badge: "bg-red-100 text-red-700 border-red-300",
      bg: "bg-red-200",
      text: "text-red-700",
      icon: AlertCircle,
    },
    replacement_opportunity: {
      label: "Opportunity",
      badge: "bg-amber-100 text-amber-700 border-amber-300",
      bg: "bg-amber-200",
      text: "text-amber-700",
      icon: AlertTriangle,
    },
    suitability_review: {
      label: "Suitability",
      badge: "bg-purple-100 text-purple-700 border-purple-300",
      bg: "bg-purple-200",
      text: "text-purple-700",
      icon: Info,
    },
    income_planning: {
      label: "Income Planning",
      badge: "bg-amber-100 text-amber-700 border-amber-300",
      bg: "bg-amber-200",
      text: "text-amber-700",
      icon: DollarSign,
    },
    missing_info: {
      label: "Missing Info",
      badge: "bg-red-100 text-red-700 border-red-300",
      bg: "bg-red-200",
      text: "text-red-700",
      icon: AlertTriangle,
    },
  };
  return map[type] ?? map.missing_info;
}

function getAlertEvidence(a: RenewalAlert): string[] {
  const ev: string[] = [];
  if (
    a.alertType === "replacement_recommended" ||
    a.alertType === "replacement_opportunity"
  ) {
    const cr = parseFloat(a.currentRate),
      rr = parseFloat(a.renewalRate);
    if (!isNaN(cr) && !isNaN(rr) && cr > rr) {
      ev.push(
        `Rate dropping ${(((cr - rr) / cr) * 100).toFixed(1)}% (${a.currentRate} → ${a.renewalRate})`,
      );
    }
    if (a.isMinRate) ev.push("Renewing at guaranteed minimum rate");
    if (a.daysUntilRenewal <= 30)
      ev.push(`Urgent: Only ${a.daysUntilRenewal} days until renewal`);
    const val = parseFloat(a.currentValue.replace(/[$,]/g, ""));
    if (!isNaN(cr) && !isNaN(rr) && !isNaN(val)) {
      ev.push(
        `Annual income impact: $${Math.round((val * (cr - rr)) / 100).toLocaleString()}`,
      );
    }
  } else if (a.alertType === "suitability_review") {
    ev.push("Annual suitability review period");
    ev.push("Client objectives and risk tolerance confirmation needed");
  } else if (a.alertType === "income_planning") {
    ev.push("Client approaching income distribution phase");
    ev.push(`Policy value: ${a.currentValue}`);
  } else if (a.alertType === "missing_info") {
    if (a.missingFields?.length) ev.push(...a.missingFields);
    else ev.push("Data quality issues detected");
  }
  return ev;
}

function FeatureSection({
  title,
  icon: Icon,
  items,
  color,
}: {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  items: { name: string; description: string; included: boolean }[];
  color: "blue" | "green" | "purple" | "amber";
}) {
  if (!items.length) return null;
  const headerColors = {
    blue: "bg-blue-50 border-blue-200 text-blue-800",
    green: "bg-green-50 border-green-200 text-green-800",
    purple: "bg-purple-50 border-purple-200 text-purple-800",
    amber: "bg-amber-50 border-amber-200 text-amber-800",
  };
  const iconColors = {
    blue: "text-blue-600",
    green: "text-green-600",
    purple: "text-purple-600",
    amber: "text-amber-600",
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div
        className={`px-4 py-3 border-b flex items-center gap-2 ${headerColors[color]}`}
      >
        <Icon className={`h-4 w-4 ${iconColors[color]}`} />
        <h5 className="text-sm font-bold">{title}</h5>
        <Badge variant="outline" className="ml-auto text-xs">
          {items.length}
        </Badge>
      </div>
      <div className="p-4 space-y-2">
        {items.map((item) => (
          <div key={item.name} className="flex items-start gap-2">
            {item.included ? (
              <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
            ) : (
              <XCircle className="h-4 w-4 text-slate-300 mt-0.5 shrink-0" />
            )}
            <div>
              <div className="text-sm font-medium text-slate-900">
                {item.name}
              </div>
              <div className="text-xs text-slate-500">{item.description}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
