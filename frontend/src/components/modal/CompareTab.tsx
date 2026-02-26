import { useState, useEffect } from "react";
import type {
  ComparisonParameters,
  ComparisonData,
  ProductOption,
  VisualizationProduct,
} from "@/types/alert-detail";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ChevronLeft,
  CheckCircle2,
  XCircle,
  Loader2,
  Eye,
  RefreshCw,
  User,
  Pencil,
  AlertCircle,
} from "lucide-react";
import { ParametersView } from "./ParametersView";
import { ProductShelfModal } from "./ProductShelfModal";
import { InteractiveComparisonCharts } from "./InteractiveComparisonCharts";
import { fetchProductShelf } from "@/api/alert-detail";
import { getVisualizationProducts } from "@/api/compare";

type CompareView = "parameters" | "overview";

interface CompareTabProps {
  parameters: ComparisonParameters;
  comparisonData: ComparisonData | null;
  clientName: string;
  policyValue: string;
  isLoading: boolean;
  onParametersChange: (params: ComparisonParameters) => void;
  onRunComparison: () => void;
  onRecompareWithProducts: (products: ProductOption[]) => void;
  onEditProfile?: () => void;
  startOnParameters?: boolean;
  onNext?: () => void;
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
  onNext,
}: CompareTabProps) {
  const [view, setView] = useState<CompareView>(
    startOnParameters ? "parameters" : "overview",
  );
  const [shelfOpen, setShelfOpen] = useState(false);
  const [hasRun, setHasRun] = useState(false);
  const [shelfProducts, setShelfProducts] = useState<ProductOption[]>([]);
  const [loadingShelf, setLoadingShelf] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<ProductOption | null>(null);
  const [vizProducts, setVizProducts] = useState<VisualizationProduct[]>([]);
  const [vizLoading, setVizLoading] = useState(true);

  const handleProceed = () => {
    onRunComparison();
    setView("overview");
  };

  useEffect(() => {
    if (!hasRun && !comparisonData && !isLoading) {
      setHasRun(true);
      onRunComparison();
    }
  }, [hasRun, comparisonData, isLoading, onRunComparison]);

  useEffect(() => {
    if (shelfOpen && shelfProducts.length === 0 && !loadingShelf) {
      setLoadingShelf(true);
      fetchProductShelf()
        .then(setShelfProducts)
        .catch((err) => console.error("Failed to load product shelf:", err))
        .finally(() => setLoadingShelf(false));
    }
  }, [shelfOpen, shelfProducts.length, loadingShelf]);

  // Load visualization data for charts
  useEffect(() => {
    if (comparisonData) {
      setVizLoading(true);
      getVisualizationProducts()
        .then((allVizProducts) => {
          // Filter to only the 4 products we're comparing
          const allProducts = [comparisonData.current, ...comparisonData.alternatives];
          const matched = allProducts
            .map(p => allVizProducts.find(v => v.name === p.name))
            .filter((v): v is VisualizationProduct => v !== undefined);
          setVizProducts(matched);
          setVizLoading(false);
        })
        .catch((err) => {
          console.error("Failed to load visualization data:", err);
          setVizLoading(false);
        });
    }
  }, [comparisonData]);

  const handleShelfSelect = (products: ProductOption[]) => {
    onRecompareWithProducts(products);
  };

  // LAT Indicator Component
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

  const allProducts = [comparisonData.current, ...comparisonData.alternatives];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => setView("parameters")}
          className="text-slate-600"
        >
          <ChevronLeft className="h-4 w-4 mr-1" /> Back to Parameters
        </Button>
        <Button variant="outline" onClick={() => setShelfOpen(true)}>
          <RefreshCw className="h-4 w-4 mr-2" />
          See Other Products
        </Button>
      </div>

      <ProductShelfModal
        open={shelfOpen}
        onClose={() => setShelfOpen(false)}
        products={shelfProducts}
        onDone={handleShelfSelect}
        selectedProducts={comparisonData.alternatives}
      />

      {/* Edit Profile Banner */}
      {onEditProfile && (
        <div className="flex items-center justify-between p-4 bg-indigo-50 border border-indigo-200 rounded-xl">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-indigo-100 flex items-center justify-center">
              <User className="h-5 w-5 text-indigo-600" />
            </div>
            <p className="text-sm text-slate-700">
              Product searches and filtering are based on the current client profile data on record.
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

      {/* Comparison Table */}
      <div className="border rounded-lg overflow-hidden bg-white">
        <table className="w-full">
          <thead>
            <tr className="bg-slate-50 border-b">
              <th className="text-left p-4 text-sm font-semibold text-slate-700 w-48"></th>
              {allProducts.map((product, idx) => (
                <th key={idx} className="text-left p-4 border-l align-top">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge variant="outline" className={idx === 0 ? "bg-slate-100 text-slate-700 border-slate-300" : "bg-blue-100 text-blue-700 border-blue-300"}>
                        {idx === 0 ? "Current Policy" : `Alternative ${idx}`}
                      </Badge>
                      <button
                        onClick={() => setSelectedProduct(product)}
                        className="text-blue-600 hover:text-blue-800 text-xs font-medium flex items-center gap-1"
                      >
                        <Eye className="h-3.5 w-3.5" /> Details
                      </button>
                    </div>
                    <div>
                      <div className="font-bold text-slate-900 text-base">{product.name}</div>
                      <div className="text-xs text-slate-600 mt-0.5">{product.carrier}</div>
                    </div>
                    {/* Pros */}
                    {product.features && product.features.length > 0 && (
                      <div className="space-y-1.5">
                        {product.features.slice(0, 3).map((feature, i) => (
                          <div key={i} className="text-xs text-green-700 flex items-start gap-1.5">
                            <CheckCircle2 className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                            <span>{feature}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    {/* Cons */}
                    {product.cons && product.cons.length > 0 && (
                      <div className="space-y-1.5">
                        {product.cons.slice(0, 3).map((con, i) => (
                          <div key={i} className="text-xs text-red-700 flex items-start gap-1.5">
                            <XCircle className="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                            <span>{con}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Rate */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Current Rate</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm font-bold text-slate-900">{product.rate}</td>
              ))}
            </tr>
            {/* Term */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Rate Guarantee Term</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.term || "—"}</td>
              ))}
            </tr>
            {/* Premium Bonus */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Premium Bonus</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm font-semibold">{product.premiumBonus || "None"}</td>
              ))}
            </tr>
            {/* Surrender Period */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Surrender Period</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.surrenderPeriod || "—"}</td>
              ))}
            </tr>
            {/* Surrender Charge */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Surrender Charge Schedule</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.surrenderCharge || "—"}</td>
              ))}
            </tr>
            {/* Free Withdrawal */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Penalty-Free Withdrawal</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.freeWithdrawal || "—"}</td>
              ))}
            </tr>
            {/* Death Benefit */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Death Benefit</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.deathBenefit || "—"}</td>
              ))}
            </tr>
            {/* Guaranteed Min Rate */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Guaranteed Minimum Rate</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.guaranteedMinRate || "—"}</td>
              ))}
            </tr>
            {/* Liquidity */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Liquidity Features</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.liquidity || "—"}</td>
              ))}
            </tr>
            {/* MVA Penalty */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Market Value Adjustment</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">{product.mvaPenalty || "—"}</td>
              ))}
            </tr>
            {/* Riders */}
            <tr className="border-b hover:bg-slate-50 transition-colors">
              <td className="p-4 text-sm font-medium text-slate-700">Available Riders</td>
              {allProducts.map((product, idx) => (
                <td key={idx} className="p-4 border-l text-sm">
                  {product.riders && product.riders.length > 0 ? (
                    <ul className="space-y-0.5">
                      {product.riders.map((rider, i) => (
                        <li key={i} className="text-xs">• {rider}</li>
                      ))}
                    </ul>
                  ) : "—"}
                </td>
              ))}
            </tr>
            {/* Licensing/Appointment - Highlighted */}
            <tr className="border-b bg-amber-50">
              <td className="p-4 text-sm font-semibold text-slate-900">
                Licensing & Appointment Status
              </td>
              {allProducts.map((product, idx) => {
                const isApproved = product.licensingApproved === true;
                return (
                  <td key={idx} className="p-4 border-l">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <LATIndicator
                          letter="L"
                          label={isApproved ? "Licensed" : "License Required"}
                          isActive={isApproved}
                        />
                        <LATIndicator
                          letter="A"
                          label={isApproved ? "Carrier Appointment Active" : "Appointment Required"}
                          isActive={isApproved}
                        />
                        <LATIndicator
                          letter="T"
                          label={isApproved ? "Training Completed" : "Training Required"}
                          isActive={isApproved}
                        />
                      </div>
                      {isApproved ? (
                        <div className="text-xs text-green-700 font-medium">
                          ✓ Ready to sell
                        </div>
                      ) : (
                        <div className="text-xs text-red-700 font-medium">
                          ✗ {product.licensingDetails || "Action Required"}
                        </div>
                      )}
                    </div>
                  </td>
                );
              })}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Interactive Visualization Charts */}
      {vizLoading ? (
        <div className="flex items-center justify-center py-12 border rounded-lg bg-slate-50">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
          <span className="ml-2 text-sm text-slate-600">
            Loading visualization data...
          </span>
        </div>
      ) : (
        <InteractiveComparisonCharts products={vizProducts} primaryGoal={parameters.financialObjectives} />
      )}

      {/* 1035 Exchange / Replacement Transaction */}
      <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-300 rounded-xl">
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 rounded-xl bg-purple-600 text-white flex items-center justify-center flex-shrink-0">
            <RefreshCw className="h-6 w-6" />
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-lg text-slate-900 mb-1">1035 Exchange / Replacement Transaction</h4>
            <p className="text-sm text-slate-600 mb-4">
              Moving to new carrier - additional documentation and compliance requirements apply
            </p>
            
            <div className="grid grid-cols-3 gap-4">
              {/* Requirements */}
              <div className="bg-white/80 backdrop-blur rounded-lg p-4 border border-slate-200">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="h-4 w-4 text-blue-600" />
                  <h5 className="font-semibold text-sm text-slate-900">Requirements</h5>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <span>Full suitability review</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <span>Client acknowledgment forms</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <span>Carrier approval process</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <CheckCircle2 className="h-3.5 w-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <span>State replacement forms</span>
                  </li>
                </ul>
              </div>

              {/* Restrictions */}
              <div className="bg-white/80 backdrop-blur rounded-lg p-4 border border-slate-200">
                <div className="flex items-center gap-2 mb-3">
                  <XCircle className="h-4 w-4 text-amber-600" />
                  <h5 className="font-semibold text-sm text-slate-900">Restrictions</h5>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <XCircle className="h-3.5 w-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <span>New surrender period applies</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <XCircle className="h-3.5 w-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <span>MVA may apply during transition</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <XCircle className="h-3.5 w-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <span>Bonus vesting schedules</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <XCircle className="h-3.5 w-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <span>Age and health limitations</span>
                  </li>
                </ul>
              </div>

              {/* Regulatory Notes */}
              <div className="bg-white/80 backdrop-blur rounded-lg p-4 border border-slate-200">
                <div className="flex items-center gap-2 mb-3">
                  <AlertCircle className="h-4 w-4 text-purple-600" />
                  <h5 className="font-semibold text-sm text-slate-900">Regulatory Notes</h5>
                </div>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <div className="h-1.5 w-1.5 rounded-full bg-purple-600 flex-shrink-0 mt-1.5" />
                    <span>FINRA Rule 2330 compliance</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <div className="h-1.5 w-1.5 rounded-full bg-purple-600 flex-shrink-0 mt-1.5" />
                    <span>State replacement regulations</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <div className="h-1.5 w-1.5 rounded-full bg-purple-600 flex-shrink-0 mt-1.5" />
                    <span>Best interest standard</span>
                  </li>
                  <li className="flex items-start gap-2 text-xs text-slate-700">
                    <div className="h-1.5 w-1.5 rounded-full bg-purple-600 flex-shrink-0 mt-1.5" />
                    <span>Documentation retention</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedProduct(null)}>
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-slate-900">{selectedProduct.name}</h3>
              <button onClick={() => setSelectedProduct(null)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>
            <div className="space-y-3 text-sm">
              <div><span className="font-medium">Carrier:</span> {selectedProduct.carrier}</div>
              <div><span className="font-medium">Rate:</span> {selectedProduct.rate}</div>
              <div><span className="font-medium">Term:</span> {selectedProduct.term}</div>
              {selectedProduct.premiumBonus && <div><span className="font-medium">Premium Bonus:</span> {selectedProduct.premiumBonus}</div>}
              {selectedProduct.riders && selectedProduct.riders.length > 0 && (
                <div>
                  <span className="font-medium">Riders:</span>
                  <ul className="ml-4 mt-1 space-y-1">
                    {selectedProduct.riders.map((rider, i) => <li key={i}>• {rider}</li>)}
                  </ul>
                </div>
              )}
              {selectedProduct.features && selectedProduct.features.length > 0 && (
                <div>
                  <span className="font-medium">Features:</span>
                  <ul className="ml-4 mt-1 space-y-1">
                    {selectedProduct.features.map((feature, i) => <li key={i}>• {feature}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Continue Button */}
      {onNext && (
        <div className="flex justify-end pt-4">
          <button
            onClick={onNext}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            Continue to Action →
          </button>
        </div>
      )}
    </div>
  );
}
