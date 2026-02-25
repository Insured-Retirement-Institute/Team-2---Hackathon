import { useState } from "react";
import type { ComparisonParameters } from "@/types/alert-detail";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Sparkles,
  Info,
  ChevronRight,
  User,
  DollarSign,
  Target,
  TrendingUp,
  TrendingDown,
  Home,
  Shield,
  Stethoscope,
  Wallet,
  PiggyBank,
  BarChart3,
  Clock,
  Briefcase,
  Building2,
  Landmark,
  Calendar,
  Heart,
} from "lucide-react";

interface ParametersViewProps {
  parameters: ComparisonParameters;
  clientName: string;
  policyValue: string;
  onChange: (p: ComparisonParameters) => void;
  onProceed: () => void;
  onSkip: () => void;
}

const TAX_BRACKETS = [
  { value: "10%", label: "10%", range: "$0 - $11,000" },
  { value: "12%", label: "12%", range: "$11,001 - $44,725" },
  { value: "22%", label: "22%", range: "$44,726 - $95,375" },
  { value: "24%", label: "24%", range: "$95,376 - $182,100" },
  { value: "32%", label: "32%", range: "$182,101 - $231,250" },
  { value: "35%", label: "35%", range: "$231,251 - $578,125" },
  { value: "37%", label: "37%", range: "$578,126+" },
];

const FINANCIAL_OBJECTIVES = [
  {
    value: "income",
    label: "Income",
    desc: "Generate regular income",
    icon: DollarSign,
  },
  {
    value: "accumulation",
    label: "Accumulation",
    desc: "Grow assets over time",
    icon: TrendingUp,
  },
  {
    value: "death-benefit",
    label: "Death Benefit",
    desc: "Legacy protection",
    icon: Shield,
  },
];

const DISTRIBUTION_PLANS = [
  { value: "free-withdrawals", label: "Free Withdrawals", icon: Wallet },
  { value: "rmds", label: "RMDs", icon: Calendar },
  { value: "lump-sum", label: "Lump Sum", icon: PiggyBank },
  { value: "beneficiaries", label: "Beneficiaries", icon: Heart },
  { value: "annuitize", label: "Annuitize", icon: BarChart3 },
  { value: "income-rider", label: "Income Rider", icon: TrendingUp },
];

const EMPLOYMENT_OPTIONS = [
  { value: "retired", label: "Retired", icon: Home, color: "blue" as const },
  {
    value: "employed",
    label: "Employed",
    icon: Briefcase,
    color: "green" as const,
  },
  {
    value: "self-employed",
    label: "Self-Employed",
    icon: Building2,
    color: "purple" as const,
  },
  {
    value: "not-employed",
    label: "Not Employed",
    icon: Clock,
    color: "slate" as const,
  },
];

const TIME_HORIZONS = [
  { value: "less-1", label: "< 1 Year" },
  { value: "1-5", label: "1-5 Years" },
  { value: "6-9", label: "6-9 Years" },
  { value: "10-plus", label: "10+ Years" },
  { value: "none", label: "None Anticipated" },
];

function Toggle({
  value,
  current,
  onChange,
  label,
}: {
  value: "yes" | "no";
  current: "yes" | "no";
  onChange: (v: "yes" | "no") => void;
  label: string;
}) {
  const active = current === value;
  return (
    <button
      onClick={() => onChange(value)}
      className={`px-6 py-2 rounded-lg font-semibold text-sm transition-all ${
        active
          ? value === "yes"
            ? "bg-green-600 text-white shadow-md"
            : "bg-slate-600 text-white shadow-md"
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      {label}
    </button>
  );
}

function SectionHeader({
  icon: Icon,
  title,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
}) {
  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-5 shadow-lg flex items-center gap-3">
      <Icon className="h-6 w-6 text-white" />
      <h3 className="text-lg font-bold text-white">{title}</h3>
    </div>
  );
}

function CurrencyInput({
  id,
  value,
  onChange,
  hint,
}: {
  id: string;
  value: string;
  onChange: (v: string) => void;
  hint?: string;
}) {
  return (
    <div>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-semibold">
          $
        </span>
        <Input
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="pl-7 h-11 border-slate-300 focus:border-blue-500"
          placeholder="0"
        />
      </div>
      {hint && <p className="text-xs text-slate-500 mt-1.5">{hint}</p>}
    </div>
  );
}

export function ParametersView({
  parameters,
  clientName,
  policyValue,
  onChange,
  onProceed,
  onSkip,
}: ParametersViewProps) {
  const [hasEdited, setHasEdited] = useState(false);
  const update = (key: keyof ComparisonParameters, value: string) => {
    onChange({ ...parameters, [key]: value });
    setHasEdited(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
          <Sparkles className="h-6 w-6 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-slate-900">
            Review Comparison Parameters
          </h2>
          <p className="text-sm text-slate-600">
            {clientName} • {policyValue}
          </p>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
        <Info className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="text-sm text-slate-700">
          <span className="font-semibold text-slate-900">
            These parameters influence comparison results.
          </span>{" "}
          Pre-filled from client profile. Review and adjust if needed.
        </div>
      </div>

      {/* PROFILE */}
      <SectionHeader icon={User} title="Profile" />
      <div className="grid grid-cols-3 gap-4">
        {[
          {
            key: "residesInNursingHome" as const,
            label: "Nursing Home",
            sub: "Current residence",
            icon: Home,
            color: "blue" as const,
          },
          {
            key: "hasLongTermCareInsurance" as const,
            label: "LTC Insurance",
            sub: "Long-term care coverage",
            icon: Shield,
            color: "purple" as const,
          },
          {
            key: "hasMedicareSupplemental" as const,
            label: "Medicare Supp",
            sub: "Supplemental coverage",
            icon: Stethoscope,
            color: "green" as const,
          },
        ].map((item) => {
          const Ic = item.icon;
          const bgMap = {
            blue: "bg-blue-100",
            purple: "bg-purple-100",
            green: "bg-green-100",
          };
          const txtMap = {
            blue: "text-blue-700",
            purple: "text-purple-700",
            green: "text-green-700",
          };
          return (
            <div
              key={item.key}
              className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3 mb-4">
                <div
                  className={`h-10 w-10 rounded-lg ${bgMap[item.color]} flex items-center justify-center`}
                >
                  <Ic className={`h-5 w-5 ${txtMap[item.color]}`} />
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 text-sm">
                    {item.label}
                  </h4>
                  <p className="text-xs text-slate-600">{item.sub}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Toggle
                  value="yes"
                  current={parameters[item.key]}
                  onChange={(v) => update(item.key, v)}
                  label="Yes"
                />
                <Toggle
                  value="no"
                  current={parameters[item.key]}
                  onChange={(v) => update(item.key, v)}
                  label="No"
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* SUITABILITY */}
      <SectionHeader icon={DollarSign} title="Suitability" />

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h4 className="font-bold text-slate-900 mb-5">Financial Information</h4>
        <div className="grid grid-cols-3 gap-5">
          <div>
            <label className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-green-600" />
              Gross Income
            </label>
            <CurrencyInput
              id="gi"
              value={parameters.grossIncome}
              onChange={(v) => update("grossIncome", v)}
              hint="Social Security, salary, pension"
            />
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <Wallet className="h-4 w-4 text-blue-600" />
              Disposable Income
            </label>
            <CurrencyInput
              id="di"
              value={parameters.disposableIncome}
              onChange={(v) => update("disposableIncome", v)}
            />
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <Landmark className="h-4 w-4 text-purple-600" />
              Tax Bracket
            </label>
            <Select
              value={parameters.taxBracket}
              onValueChange={(v) => update("taxBracket", v)}
            >
              <SelectTrigger className="h-11 border-slate-300">
                <SelectValue placeholder="Select bracket" />
              </SelectTrigger>
              <SelectContent>
                {TAX_BRACKETS.map((b) => (
                  <SelectItem key={b.value} value={b.value}>
                    <span className="font-semibold">{b.label}</span>{" "}
                    <span className="text-xs text-slate-500 ml-2">
                      {b.range}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <PiggyBank className="h-4 w-4 text-cyan-600" />
              Liquid Assets
            </label>
            <CurrencyInput
              id="la"
              value={parameters.householdLiquidAssets}
              onChange={(v) => update("householdLiquidAssets", v)}
              hint="Checking, savings, stocks, bonds"
            />
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <Home className="h-4 w-4 text-orange-600" />
              Monthly Expenses
            </label>
            <CurrencyInput
              id="me"
              value={parameters.monthlyLivingExpenses}
              onChange={(v) => update("monthlyLivingExpenses", v)}
            />
          </div>
          <div>
            <label className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-indigo-600" />
              Total Annuity Value
            </label>
            <CurrencyInput
              id="av"
              value={parameters.totalAnnuityValue}
              onChange={(v) => update("totalAnnuityValue", v)}
            />
          </div>
          <div className="col-span-3">
            <label className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              Household Net Worth
            </label>
            <div className="max-w-sm">
              <CurrencyInput
                id="nw"
                value={parameters.householdNetWorth}
                onChange={(v) => update("householdNetWorth", v)}
                hint="Include annuity, exclude primary residence"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Anticipated Changes */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-5">
          <TrendingDown className="h-5 w-5 text-amber-600" />
          <h4 className="font-bold text-slate-900">
            Anticipated Changes During Contract Period
          </h4>
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[
            {
              key: "anticipateExpenseIncrease" as const,
              label: "Expense Increase?",
              sub: "Significant rise in living costs",
              icon: TrendingUp,
              activeColor: "amber" as const,
            },
            {
              key: "anticipateIncomeDecrease" as const,
              label: "Income Decrease?",
              sub: "Reduction in regular income",
              icon: TrendingDown,
              activeColor: "red" as const,
            },
            {
              key: "anticipateLiquidAssetDecrease" as const,
              label: "Asset Decrease?",
              sub: "Drop in liquid assets",
              icon: Wallet,
              activeColor: "orange" as const,
            },
          ].map((item) => {
            const Ic = item.icon;
            const isYes = parameters[item.key] === "yes";
            const borderMap = {
              amber: "border-amber-500 bg-amber-50",
              red: "border-red-500 bg-red-50",
              orange: "border-orange-500 bg-orange-50",
            };
            const iconBgMap = {
              amber: "bg-amber-200",
              red: "bg-red-200",
              orange: "bg-orange-200",
            };
            const iconTxtMap = {
              amber: "text-amber-700",
              red: "text-red-700",
              orange: "text-orange-700",
            };
            return (
              <div
                key={item.key}
                className={`p-4 rounded-xl border-2 transition-all ${isYes ? borderMap[item.activeColor] : "border-slate-200 bg-slate-50"}`}
              >
                <div className="flex items-start gap-3 mb-3">
                  <div
                    className={`h-8 w-8 rounded-lg flex items-center justify-center ${isYes ? iconBgMap[item.activeColor] : "bg-slate-200"}`}
                  >
                    <Ic
                      className={`h-4 w-4 ${isYes ? iconTxtMap[item.activeColor] : "text-slate-600"}`}
                    />
                  </div>
                  <div>
                    <h5 className="font-semibold text-sm text-slate-900">
                      {item.label}
                    </h5>
                    <p className="text-xs text-slate-600">{item.sub}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Toggle
                    value="yes"
                    current={parameters[item.key]}
                    onChange={(v) => update(item.key, v)}
                    label="Yes"
                  />
                  <Toggle
                    value="no"
                    current={parameters[item.key]}
                    onChange={(v) => update(item.key, v)}
                    label="No"
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* OBJECTIVES */}
      <SectionHeader icon={Target} title="Objectives & Planning" />

      {/* Financial Objectives */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h4 className="font-bold text-slate-900 mb-4">Financial Objectives</h4>
        <div className="grid grid-cols-3 gap-4">
          {FINANCIAL_OBJECTIVES.map((obj) => {
            const Ic = obj.icon;
            const sel = parameters.financialObjectives === obj.value;
            return (
              <button
                key={obj.value}
                onClick={() => update("financialObjectives", obj.value)}
                className={`p-5 rounded-xl border-2 transition-all text-left ${sel ? "border-blue-500 bg-blue-50 shadow-md" : "border-slate-200 hover:border-slate-300"}`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <div
                    className={`h-10 w-10 rounded-lg flex items-center justify-center ${sel ? "bg-blue-600" : "bg-slate-100"}`}
                  >
                    <Ic
                      className={`h-5 w-5 ${sel ? "text-white" : "text-slate-600"}`}
                    />
                  </div>
                  <h5
                    className={`font-bold text-sm ${sel ? "text-blue-900" : "text-slate-900"}`}
                  >
                    {obj.label}
                  </h5>
                </div>
                <p className="text-xs text-slate-600">{obj.desc}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Distribution Plan */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h4 className="font-bold text-slate-900 mb-4">Distribution Plan</h4>
        <div className="grid grid-cols-6 gap-3">
          {DISTRIBUTION_PLANS.map((plan) => {
            const Ic = plan.icon;
            const sel = parameters.distributionPlan === plan.value;
            return (
              <button
                key={plan.value}
                onClick={() => update("distributionPlan", plan.value)}
                className={`p-4 rounded-lg border-2 transition-all ${sel ? "border-indigo-500 bg-indigo-50 shadow-md" : "border-slate-200 hover:border-slate-300"}`}
              >
                <div
                  className={`h-8 w-8 rounded-lg mx-auto mb-2 flex items-center justify-center ${sel ? "bg-indigo-600" : "bg-slate-100"}`}
                >
                  <Ic
                    className={`h-4 w-4 ${sel ? "text-white" : "text-slate-600"}`}
                  />
                </div>
                <p
                  className={`text-xs font-semibold text-center ${sel ? "text-indigo-900" : "text-slate-700"}`}
                >
                  {plan.label}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Employment Status */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
        <h4 className="font-bold text-slate-900 mb-4">Employment Status</h4>
        <div className="grid grid-cols-4 gap-4">
          {EMPLOYMENT_OPTIONS.map((emp) => {
            const Ic = emp.icon;
            const sel = parameters.employmentStatus === emp.value;
            const colors = {
              blue: {
                border: "border-blue-500",
                bg: "bg-blue-50",
                iconBg: "bg-blue-600",
                text: "text-blue-900",
              },
              green: {
                border: "border-green-500",
                bg: "bg-green-50",
                iconBg: "bg-green-600",
                text: "text-green-900",
              },
              purple: {
                border: "border-purple-500",
                bg: "bg-purple-50",
                iconBg: "bg-purple-600",
                text: "text-purple-900",
              },
              slate: {
                border: "border-slate-500",
                bg: "bg-slate-50",
                iconBg: "bg-slate-600",
                text: "text-slate-900",
              },
            }[emp.color];
            return (
              <button
                key={emp.value}
                onClick={() => update("employmentStatus", emp.value)}
                className={`p-5 rounded-xl border-2 transition-all ${sel ? `${colors.border} ${colors.bg} shadow-md` : "border-slate-200 hover:border-slate-300"}`}
              >
                <div
                  className={`h-12 w-12 rounded-xl mx-auto mb-3 flex items-center justify-center ${sel ? colors.iconBg : "bg-slate-100"}`}
                >
                  <Ic
                    className={`h-6 w-6 ${sel ? "text-white" : "text-slate-600"}`}
                  />
                </div>
                <p
                  className={`font-bold text-sm text-center ${sel ? colors.text : "text-slate-900"}`}
                >
                  {emp.label}
                </p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Additional selects */}
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-4">
          <SelectCard
            label="Owned Assets"
            value={parameters.ownedAssets}
            onChange={(v) => update("ownedAssets", v)}
            options={[
              { value: "cds", label: "CDs" },
              { value: "annuities", label: "Annuities" },
              { value: "life-insurance", label: "Life Insurance" },
              { value: "stocks-bonds", label: "Stocks/Bonds/Mutual Funds" },
              { value: "none", label: "None" },
            ]}
          />
          <SelectCard
            label="Time to First Distribution"
            value={parameters.timeToFirstDistribution}
            onChange={(v) => update("timeToFirstDistribution", v)}
            options={TIME_HORIZONS}
          />
          <SelectCard
            label="Expected Holding Period"
            value={parameters.expectedHoldingPeriod}
            onChange={(v) => update("expectedHoldingPeriod", v)}
            options={TIME_HORIZONS}
          />
        </div>
        <div className="space-y-4">
          <SelectCard
            label="Source of Funds"
            value={parameters.sourceOfFunds}
            onChange={(v) => update("sourceOfFunds", v)}
            options={[
              { value: "annuity", label: "Annuity" },
              { value: "life-insurance", label: "Life Insurance" },
              { value: "cd", label: "CD" },
              { value: "savings", label: "Savings/Checking" },
              { value: "stocks-bonds", label: "Stocks/Bonds/Mutual Funds" },
            ]}
          />
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
            <h5 className="text-sm font-semibold text-slate-700 mb-3">
              Means-Tested Government Benefits?
            </h5>
            <div className="flex gap-3">
              <Toggle
                value="yes"
                current={parameters.applyToMeansTestedBenefits}
                onChange={(v) => update("applyToMeansTestedBenefits", v)}
                label="Yes"
              />
              <Toggle
                value="no"
                current={parameters.applyToMeansTestedBenefits}
                onChange={(v) => update("applyToMeansTestedBenefits", v)}
                label="No"
              />
            </div>
            <p className="text-xs text-slate-500 mt-3">
              Including medical or veterans aid
            </p>
          </div>
        </div>
      </div>

      <Separator className="my-4" />

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <div
            className={`h-2.5 w-2.5 rounded-full ${hasEdited ? "bg-blue-500 animate-pulse" : "bg-green-500"}`}
          />
          <span
            className={
              hasEdited ? "font-semibold text-slate-900" : "text-slate-600"
            }
          >
            {hasEdited ? "Parameters modified" : "Using default parameters"}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            onClick={onSkip}
            className="text-slate-600 h-11 px-6"
          >
            Skip & Use Defaults
          </Button>
          <Button
            onClick={onProceed}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold px-8 h-11 shadow-lg shadow-blue-500/30"
          >
            View Comparisons <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function SelectCard({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
      <label className="text-sm font-semibold text-slate-700 mb-3 block">
        {label}
      </label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="h-11 border-slate-300">
          <SelectValue placeholder={`Select ${label.toLowerCase()}`} />
        </SelectTrigger>
        <SelectContent>
          {options.map((o) => (
            <SelectItem key={o.value} value={o.value}>
              {o.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
