import { useState, useEffect } from "react";
import type {
  ComparisonParameters,
  ComparisonData,
  ProductOption,
  VisualizationProduct,
} from "@/types/alert-detail";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  ChevronLeft,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Loader2,
  TrendingUp,
  Shield,
  DollarSign,
  Zap,
  ArrowUp,
  ArrowDown,
  AlertTriangle,
  Gift,
  RefreshCw,
  FileText,
  Info,
  User,
  Pencil,
} from "lucide-react";
import { ParametersView } from "./ParametersView";
import { InteractiveComparisonCharts } from "./InteractiveComparisonCharts";
import { ProductShelfModal } from "./ProductShelfModal";
import { fetchProductShelf, fetchVisualization } from "@/api/alert-detail";

type CompareView = "parameters" | "overview" | "detailed";

interface CompareTabProps {
  parameters: ComparisonParameters;
  comparisonData: ComparisonData | null;
  clientName: string;
  policyValue: string;
  isLoading: boolean;
  onParametersChange: (params: ComparisonParameters) => void;
  onRunComparison: () => void;
  onRecompareWithProducts: (productIds: string[]) => void;
  onEditProfile?: () => void;
  startOnParameters?: boolean;
}

export function CompareTab({
  parameters,
  comparisonData,
  clientName,
  policyValue,
  isLoading,
  onParametersChange,
  onRunComparison,
  onRecompareWithProducts,
  onEditProfile,
  startOnParameters,
}: CompareTabProps) {
  const [view, setView] = useState<CompareView>(
    startOnParameters ? "parameters" : "overview",
  );
  const [shelfOpen, setShelfOpen] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [shelfProducts, setShelfProducts] = useState<ProductOption[]>([]);
  const [loadingShelf, setLoadingShelf] = useState(false);

  const handleProceed = () => {
    onRunComparison();
    setView("overview");
  };

  // Auto-run comparison on first render if not already done
  useEffect(() => {
    if (!hasRun && !comparisonData && !isLoading) {
      setHasRun(true);
      onRunComparison();
    }
  }, [hasRun, comparisonData, isLoading, onRunComparison]);

  // Load product shelf when modal opens
  useEffect(() => {
    if (shelfOpen && shelfProducts.length === 0 && !loadingShelf) {
      setLoadingShelf(true);
      fetchProductShelf()
        .then(setShelfProducts)
        .catch((err) => console.error("Failed to load product shelf:", err))
        .finally(() => setLoadingShelf(false));
    }
  }, [shelfOpen, shelfProducts.length, loadingShelf]);

  const handleShelfSelect = (products: ProductOption[]) => {
    onRecompareWithProducts(products.map((p) => p.id));
  };

  if (view === "parameters") {
    return (
      <ParametersView
        parameters={parameters}
        clientName={clientName}
        policyValue={policyValue}
        onChange={onParametersChange}
        onProceed={handleProceed}
        onSkip={() => {
          onRunComparison();
          setView("overview");
        }}
      />
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        <span className="ml-3 text-slate-600">
          Running comparison analysis...
        </span>
      </div>
    );
  }

  if (!comparisonData) return null;

  if (view === "overview") {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => setView("parameters")}
            className="text-slate-600"
          >
            <ChevronLeft className="h-4 w-4 mr-1" /> Back to Parameters
          </Button>
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => setShelfOpen(true)}>
              See Other Products
            </Button>
            <Button
              variant="outline"
              onClick={() => setView("detailed")}
              className="border-blue-600 text-blue-600 hover:bg-blue-50"
            >
              View Detailed Comparison
            </Button>
          </div>
        </div>
        <ProductShelfModal
          open={shelfOpen}
          onClose={() => setShelfOpen(false)}
          products={shelfProducts}
          onDone={handleShelfSelect}
          selectedProducts={comparisonData.alternatives}
        />
        <EditProfileBanner onEditProfile={onEditProfile} />
        <ProductsOverview
          current={comparisonData.current}
          alternatives={comparisonData.alternatives}
          comparisonData={comparisonData}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Button
        variant="ghost"
        onClick={() => setView("overview")}
        className="text-slate-600"
      >
        <ChevronLeft className="h-4 w-4 mr-1" /> Back to Overview
      </Button>
      <EditProfileBanner onEditProfile={onEditProfile} />
      <h3 className="text-lg font-bold text-slate-900">
        Detailed Product Comparison
      </h3>
      <DetailedTable
        current={comparisonData.current}
        alternatives={comparisonData.alternatives}
      />
    </div>
  );
}

/* ── Edit Profile Banner ──────────────────────────────────── */
function EditProfileBanner({ onEditProfile }: { onEditProfile?: () => void }) {
  if (!onEditProfile) return null;
  return (
    <div className="flex items-center justify-between p-4 bg-indigo-50 border border-indigo-200 rounded-xl">
      <div className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-lg bg-indigo-100 flex items-center justify-center">
          <User className="h-5 w-5 text-indigo-600" />
        </div>
        <p className="text-sm text-slate-700">
          Product searches and filtering are based on the current client profile
          data on record.
        </p>
      </div>
      <button
        onClick={onEditProfile}
        className="flex items-center gap-1.5 text-sm font-semibold text-indigo-700 hover:text-indigo-900 hover:underline shrink-0"
      >
        <Pencil className="h-3.5 w-3.5" /> Edit Client Profile
      </button>
    </div>
  );
}

/* ── LAT Indicator ───────────────────────────────────────── */
function LATIndicator({
  letter,
  label,
  isActive,
}: {
  letter: string;
  label: string;
  isActive: boolean;
}) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <div
        className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-bold cursor-help ${
          isActive ? "bg-green-500 text-white" : "bg-red-500 text-white"
        }`}
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
      >
        {letter}
      </div>
      {show && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-slate-900 text-white text-xs rounded whitespace-nowrap z-10">
          {label}
          <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900" />
        </div>
      )}
    </div>
  );
}

/* ── Products Overview (Figma match) ─────────────────────── */
function ProductsOverview({
  current,
  alternatives,
  comparisonData,
}: {
  current: ProductOption;
  alternatives: ProductOption[];
  comparisonData: ComparisonData;
}) {
  const [vizProducts, setVizProducts] = useState<VisualizationProduct[]>([]);
  const [vizLoading, setVizLoading] = useState(true);

  useEffect(() => {
    const allProducts = [
      comparisonData.current,
      ...comparisonData.alternatives,
    ];
    setVizLoading(true);
    Promise.all(allProducts.map((p) => fetchVisualization(p.id))).then(
      (results) => {
        setVizProducts(results);
        setVizLoading(false);
      },
    );
  }, [comparisonData]);
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900">
          Product Comparison Overview
        </h3>
        <p className="text-sm text-slate-600 mt-1">
          Visual comparison of alternative products vs. current policy
        </p>
      </div>

      {/* Current Policy - full width */}
      <div className="border-2 border-slate-300 rounded-xl p-5 bg-slate-50">
        <div className="flex items-center justify-between mb-3">
          <div>
            <Badge
              variant="outline"
              className="bg-slate-100 text-slate-700 border-slate-300 mb-2"
            >
              Current Policy
            </Badge>
            <h4 className="text-lg font-bold text-slate-900">{current.name}</h4>
            <p className="text-sm text-slate-600">{current.carrier}</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-slate-900">
              {current.rate}
            </div>
            <div className="text-xs text-slate-500">Current Rate</div>
          </div>
        </div>
        <div className="grid grid-cols-4 gap-4 text-sm border-t border-slate-200 pt-3">
          <MetricRow
            icon={Zap}
            iconColor="text-purple-600"
            label="Term"
            value={current.term}
          />
          <MetricRow
            icon={Shield}
            iconColor="text-green-600"
            label="Min Rate"
            value={current.guaranteedMinRate}
          />
          <MetricRow
            icon={DollarSign}
            iconColor="text-emerald-600"
            label="Free Withdrawal"
            value={current.freeWithdrawal}
          />
          <div>
            <div className="text-xs text-slate-500">Surrender</div>
            <div className="font-semibold text-slate-900">
              {current.surrenderPeriod} yrs
            </div>
          </div>
        </div>
      </div>

      {/* Alternative Products - card grid */}
      <div className="grid grid-cols-3 gap-3">
        {alternatives.map((product, idx) => {
          const canSell = product.licensingApproved === true;
          return (
            <div
              key={idx}
              className={`border-2 rounded-xl p-4 ${canSell ? "border-green-200 bg-green-50/30" : "border-amber-200 bg-amber-50/30"}`}
            >
              {/* Header + LAT */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-slate-900 text-sm leading-tight">
                    {product.name}
                  </h4>
                  <p className="text-xs text-slate-600 mt-0.5">
                    {product.carrier}
                  </p>
                </div>
                <div className="flex items-center gap-1 ml-2 shrink-0">
                  <LATIndicator
                    letter="L"
                    label={canSell ? "Licensed" : "License Required"}
                    isActive={canSell}
                  />
                  <LATIndicator
                    letter="A"
                    label={
                      canSell
                        ? "Carrier Appointment Active"
                        : "Appointment Required"
                    }
                    isActive={canSell}
                  />
                  <LATIndicator
                    letter="T"
                    label={canSell ? "Training Completed" : "Training Required"}
                    isActive={canSell}
                  />
                </div>
              </div>

              {/* Status Badge */}
              <div className="mb-2">
                {canSell ? (
                  <Badge className="bg-green-600 text-white text-xs px-2 py-0.5">
                    <CheckCircle2 className="h-3 w-3 mr-1" /> Can Sell
                  </Badge>
                ) : (
                  <Badge className="bg-amber-600 text-white text-xs px-2 py-0.5">
                    <AlertCircle className="h-3 w-3 mr-1" /> Cannot Sell
                  </Badge>
                )}
              </div>

              {/* Key Metrics */}
              <div className="space-y-1.5 border-t border-slate-200 pt-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600 flex items-center gap-1">
                    <TrendingUp className="h-3.5 w-3.5 text-blue-600" /> Rate
                  </span>
                  <span className="text-sm font-bold text-slate-900">
                    {product.rate}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600 flex items-center gap-1">
                    <Shield className="h-3.5 w-3.5 text-green-600" /> Min Rate
                  </span>
                  <span className="text-sm font-semibold text-slate-700">
                    {product.guaranteedMinRate}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600 flex items-center gap-1">
                    <DollarSign className="h-3.5 w-3.5 text-emerald-600" /> Free
                    Withdrawal
                  </span>
                  <span className="text-sm font-semibold text-slate-700">
                    {product.freeWithdrawal}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600 flex items-center gap-1">
                    <Zap className="h-3.5 w-3.5 text-purple-600" /> Term
                  </span>
                  <span className="text-sm font-semibold text-slate-700">
                    {product.term}
                  </span>
                </div>
                {product.premiumBonus && (
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-600">
                      Premium Bonus
                    </span>
                    <Badge className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5">
                      {product.premiumBonus}
                    </Badge>
                  </div>
                )}
              </div>

              {/* Licensing warning */}
              {!canSell && product.licensingDetails && (
                <div className="mt-2 pt-2 border-t border-amber-200">
                  <p className="text-xs text-amber-700 leading-relaxed">
                    {product.licensingDetails}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Interactive Charts */}
      {vizLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-sm text-slate-600">
            Loading visualization data...
          </span>
        </div>
      ) : (
        <InteractiveComparisonCharts products={vizProducts} />
      )}
    </div>
  );
}

/* ── Detailed Comparison (Figma match) ────────────────────── */
function DetailedTable({
  current,
  alternatives,
}: {
  current: ProductOption;
  alternatives: ProductOption[];
}) {
  const [selectedAlt, setSelectedAlt] = useState(0);
  const alt = alternatives[selectedAlt];
  const isSameCarrier = alt.carrier === current.carrier;

  // Material differences
  const diffs: {
    label: string;
    impact: "positive" | "negative";
    desc: string;
  }[] = [];
  const cr = parseFloat(current.rate),
    ar = parseFloat(alt.rate);
  if (!isNaN(cr) && !isNaN(ar) && Math.abs(ar - cr) >= 0.25)
    diffs.push({
      label: ar > cr ? "Higher Rate" : "Lower Rate",
      impact: ar > cr ? "positive" : "negative",
      desc: `${ar > cr ? "+" : ""}${(ar - cr).toFixed(2)}% (${alt.rate} vs ${current.rate})`,
    });
  const cw = parseFloat(current.freeWithdrawal),
    aw = parseFloat(alt.freeWithdrawal);
  if (!isNaN(cw) && !isNaN(aw) && cw !== aw)
    diffs.push({
      label: aw > cw ? "Increased Liquidity" : "Reduced Liquidity",
      impact: aw > cw ? "positive" : "negative",
      desc: `${alt.freeWithdrawal} vs ${current.freeWithdrawal}`,
    });
  const cs = parseInt(current.surrenderPeriod),
    as_ = parseInt(alt.surrenderPeriod);
  if (!isNaN(cs) && !isNaN(as_) && cs !== as_)
    diffs.push({
      label: as_ < cs ? "Shorter Surrender" : "Longer Surrender",
      impact: as_ < cs ? "positive" : "negative",
      desc: `${alt.surrenderPeriod} yrs vs ${current.surrenderPeriod} yrs`,
    });
  if (alt.premiumBonus && !current.premiumBonus)
    diffs.push({
      label: "Premium Bonus Added",
      impact: "positive",
      desc: `${alt.premiumBonus} bonus on new deposits`,
    });
  if (alt.deathBenefit !== current.deathBenefit)
    diffs.push({
      label:
        alt.deathBenefit === "Enhanced"
          ? "Enhanced Death Benefit"
          : "Reduced Death Benefit",
      impact: alt.deathBenefit === "Enhanced" ? "positive" : "negative",
      desc: `${alt.deathBenefit} vs ${current.deathBenefit}`,
    });

  return (
    <div className="space-y-5">
      {/* Alt selector */}
      {alternatives.length > 1 && (
        <div className="flex gap-2 flex-wrap">
          {alternatives.map((a, idx) => (
            <Button
              key={idx}
              variant={selectedAlt === idx ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedAlt(idx)}
              className={
                selectedAlt === idx ? "bg-blue-600 hover:bg-blue-700" : ""
              }
            >
              Alternative {idx + 1}: {a.name}
            </Button>
          ))}
        </div>
      )}

      {/* Transaction type */}
      <div
        className={`border-2 rounded-xl p-5 ${isSameCarrier ? "bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-300" : "bg-gradient-to-br from-purple-50 to-pink-50 border-purple-300"}`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 ${isSameCarrier ? "bg-blue-600" : "bg-purple-600"}`}
          >
            <RefreshCw className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-lg text-slate-900 mb-1">
              {isSameCarrier
                ? "Renewal Transaction"
                : "1035 Exchange / Replacement"}
            </h4>
            <p className="text-sm text-slate-600 mb-4">
              {isSameCarrier
                ? "Same carrier — simplified process, no replacement forms required"
                : "New carrier — additional documentation and compliance requirements apply"}
            </p>
            <div className="grid grid-cols-3 gap-4">
              <InfoList
                title="Requirements"
                icon={<FileText className="h-4 w-4 text-blue-600" />}
                items={
                  isSameCarrier
                    ? [
                        "No new underwriting required",
                        "No new application paperwork",
                        "Existing carrier relationship maintained",
                      ]
                    : [
                        "State replacement forms required",
                        "Advisor must be appointed with new carrier",
                        "1035 exchange documentation required",
                        "Suitability documentation required",
                      ]
                }
                iconEl={
                  <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 shrink-0 mt-0.5" />
                }
              />
              <InfoList
                title="Restrictions"
                icon={<AlertTriangle className="h-4 w-4 text-amber-600" />}
                items={
                  isSameCarrier
                    ? [
                        "Limited to current carrier products",
                        "Must accept carrier renewal terms",
                      ]
                    : [
                        "New surrender charge period applies",
                        "Current surrender charges may apply",
                        "MVA penalties may apply",
                        "Processing 2-4 weeks",
                      ]
                }
                iconEl={
                  <XCircle className="h-3.5 w-3.5 text-amber-600 shrink-0 mt-0.5" />
                }
              />
              <InfoList
                title="Regulatory Notes"
                icon={<Info className="h-4 w-4 text-purple-600" />}
                items={
                  isSameCarrier
                    ? [
                        "Not a replacement transaction",
                        "No state replacement forms",
                        "Original contract terms continue",
                      ]
                    : [
                        "State replacement regulations apply",
                        "Carrier notification within 5 business days",
                        "20-30 day free look period on new policy",
                        "Must demonstrate client benefit",
                      ]
                }
                iconEl={
                  <div className="h-1.5 w-1.5 rounded-full bg-purple-600 shrink-0 mt-1.5" />
                }
              />
            </div>
          </div>
        </div>
      </div>

      {/* Material differences */}
      {diffs.length > 0 && (
        <div className="border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-white rounded-xl p-5">
          <h4 className="font-bold text-amber-900 mb-3 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" /> Material Differences Detected
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {diffs.map((d, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg border ${d.impact === "positive" ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}
              >
                <div className="font-semibold text-sm text-slate-900">
                  {d.label}
                </div>
                <p className="text-xs text-slate-600 mt-0.5">{d.desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Side-by-side cards */}
      <div className="grid grid-cols-2 gap-5">
        <ProductDetailCard
          product={current}
          label="Current Policy"
          variant="current"
          compareProduct={null}
        />
        <ProductDetailCard
          product={alt}
          label="Alternative Option"
          variant="alternative"
          compareProduct={current}
        />
      </div>
    </div>
  );
}

function InfoList({
  title,
  icon,
  items,
  iconEl,
}: {
  title: string;
  icon: React.ReactNode;
  items: string[];
  iconEl: React.ReactNode;
}) {
  return (
    <div className="bg-white/80 backdrop-blur rounded-lg p-4 border border-slate-200">
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h5 className="font-semibold text-sm text-slate-900">{title}</h5>
      </div>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
            {iconEl}
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ProductDetailCard({
  product,
  label,
  variant,
  compareProduct,
}: {
  product: ProductOption;
  label: string;
  variant: "current" | "alternative";
  compareProduct: ProductOption | null;
}) {
  const isAlt = variant === "alternative";
  const better = (a: string, b: string, higherIsBetter: boolean) => {
    const av = parseFloat(a),
      bv = parseFloat(b);
    if (isNaN(av) || isNaN(bv) || av === bv) return "neutral";
    return (higherIsBetter ? av > bv : av < bv) ? "positive" : "negative";
  };

  const rateResult = compareProduct
    ? better(product.rate, compareProduct.rate, true)
    : "neutral";
  const surrenderResult = compareProduct
    ? better(product.surrenderPeriod, compareProduct.surrenderPeriod, false)
    : "neutral";
  const withdrawalResult = compareProduct
    ? better(product.freeWithdrawal, compareProduct.freeWithdrawal, true)
    : "neutral";

  const cellClass = (result: string) =>
    result === "positive"
      ? "bg-green-50 border-green-200"
      : result === "negative"
        ? "bg-red-50 border-red-200"
        : "bg-white border-slate-200";

  return (
    <div
      className={`border-2 rounded-xl overflow-hidden ${isAlt ? "border-blue-300 bg-gradient-to-br from-blue-50 to-white shadow-lg" : "border-slate-300 bg-gradient-to-br from-slate-50 to-white"}`}
    >
      {/* Header */}
      <div
        className={`p-5 border-b ${isAlt ? "border-blue-200 bg-gradient-to-r from-blue-100 to-indigo-100" : "border-slate-200 bg-slate-100"}`}
      >
        <Badge
          variant={isAlt ? "default" : "outline"}
          className={
            isAlt
              ? "mb-2 bg-blue-600 text-white"
              : "mb-2 bg-slate-200 text-slate-700 border-slate-300"
          }
        >
          {label}
        </Badge>
        <h4 className="font-bold text-lg text-slate-900">{product.name}</h4>
        <div className="flex items-center gap-2 mt-1">
          <p className="text-sm text-slate-600">{product.carrier}</p>
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded ${product.licensingApproved !== false ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}
          >
            {product.licensingApproved !== false
              ? "✓ Can Sell"
              : "✗ Cannot Sell"}
          </span>
        </div>
      </div>

      <div className="p-5 space-y-4">
        {/* Rates */}
        <SectionLabel label="Rates" isAlt={isAlt} />
        <div className="space-y-2">
          <Row
            label="Current Rate"
            value={product.rate}
            className={cellClass(rateResult)}
            bold
            arrow={
              rateResult !== "neutral"
                ? rateResult === "positive"
                  ? "up"
                  : "down"
                : undefined
            }
          />
          <Row label="Guaranteed Min" value={product.guaranteedMinRate} />
          <Row label="Rate Term" value={product.term} />
        </div>

        <Separator />

        {/* Surrender */}
        <SectionLabel label="Surrender Terms" isAlt={isAlt} />
        <div className="space-y-2">
          <Row
            label="Surrender Period"
            value={`${product.surrenderPeriod} years`}
            className={cellClass(surrenderResult)}
            arrow={
              surrenderResult !== "neutral"
                ? surrenderResult === "positive"
                  ? "down"
                  : "up"
                : undefined
            }
          />
          {product.surrenderCharge && (
            <Row label="Surrender Charge" value={product.surrenderCharge} />
          )}
          <Row
            label="Free Withdrawal"
            value={product.freeWithdrawal}
            className={cellClass(withdrawalResult)}
            arrow={
              withdrawalResult !== "neutral"
                ? withdrawalResult === "positive"
                  ? "up"
                  : "down"
                : undefined
            }
          />
          {product.mvaPenalty && (
            <Row
              label="MVA Penalty"
              value={product.mvaPenalty}
              className="bg-red-50 border-red-200"
            />
          )}
        </div>

        <Separator />

        {/* Features */}
        <SectionLabel label="Features & Benefits" isAlt={isAlt} />
        <div className="space-y-2">
          {product.premiumBonus && (
            <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg border border-green-200">
              <Gift className="h-4 w-4 text-green-700 shrink-0" />
              <div>
                <span className="text-xs text-green-700 font-medium">
                  Premium Bonus
                </span>
                <div className="text-sm font-semibold text-green-900">
                  {product.premiumBonus}
                </div>
              </div>
            </div>
          )}
          <div
            className={`flex items-center gap-2 p-3 rounded-lg border ${isAlt && product.deathBenefit === "Enhanced" ? "bg-green-50 border-green-200" : "bg-white border-slate-200"}`}
          >
            <Shield className="h-4 w-4 text-slate-700 shrink-0" />
            <div>
              <span className="text-xs text-slate-600 font-medium">
                Death Benefit
              </span>
              <div className="text-sm font-semibold text-slate-900">
                {product.deathBenefit}
              </div>
            </div>
          </div>
        </div>

        {/* Riders */}
        {product.riders && product.riders.length > 0 && (
          <>
            <Separator />
            <SectionLabel label="Riders" isAlt={isAlt} />
            <div className="space-y-1.5">
              {product.riders.map((r, i) => (
                <div
                  key={i}
                  className={`flex items-center gap-2 p-2 bg-white rounded border ${isAlt ? "border-blue-200" : "border-slate-200"}`}
                >
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-600 shrink-0" />
                  <span className="text-xs text-slate-700">{r}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function SectionLabel({ label, isAlt }: { label: string; isAlt: boolean }) {
  return (
    <h5
      className={`text-xs uppercase tracking-wide font-semibold mb-1 ${isAlt ? "text-blue-700" : "text-slate-500"}`}
    >
      {label}
    </h5>
  );
}

function Row({
  label,
  value,
  className,
  bold,
  arrow,
}: {
  label: string;
  value: string;
  className?: string;
  bold?: boolean;
  arrow?: "up" | "down";
}) {
  return (
    <div
      className={`flex justify-between items-center p-3 rounded-lg border ${className || "bg-white border-slate-200"}`}
    >
      <span className="text-sm text-slate-600">{label}</span>
      <div className="flex items-center gap-2">
        {arrow === "up" && <ArrowUp className="h-4 w-4 text-green-600" />}
        {arrow === "down" && <ArrowDown className="h-4 w-4 text-green-600" />}
        <span
          className={
            bold
              ? "text-lg font-bold text-slate-900"
              : "text-sm font-semibold text-slate-900"
          }
        >
          {value}
        </span>
      </div>
    </div>
  );
}

function MetricRow({
  icon: Icon,
  iconColor,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  iconColor: string;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <Icon className={`h-3.5 w-3.5 ${iconColor}`} />
      <div>
        <div className="text-xs text-slate-500">{label}</div>
        <div className="font-semibold text-slate-900">{value}</div>
      </div>
    </div>
  );
}
