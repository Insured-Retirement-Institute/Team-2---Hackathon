import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ProductOption } from "@/types/alert-detail";
import {
  Search,
  Shield,
  DollarSign,
  Zap,
  Calendar,
  Gift,
  X,
} from "lucide-react";

interface ProductShelfModalProps {
  open: boolean;
  onClose: () => void;
  products: ProductOption[];
  onDone?: (products: ProductOption[]) => void;
  selectedProducts?: ProductOption[];
}

export function ProductShelfModal({
  open,
  onClose,
  products,
  onDone,
  selectedProducts = [],
}: ProductShelfModalProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterCarrier, setFilterCarrier] = useState("all");
  const [filterTerm, setFilterTerm] = useState("all");
  const [filterLicensing, setFilterLicensing] = useState("all");
  const [sortBy, setSortBy] = useState("rate-desc");
  const [pending, setPending] = useState<ProductOption[]>(selectedProducts);

  // Sync pending when modal opens
  const [prevOpen, setPrevOpen] = useState(false);
  if (open && !prevOpen) setPending(selectedProducts);
  if (open !== prevOpen) setPrevOpen(open);

  const toggleProduct = (product: ProductOption) => {
    setPending((prev) => {
      if (
        prev.some(
          (p) => p.name === product.name && p.carrier === product.carrier,
        )
      ) {
        return prev.filter(
          (p) => !(p.name === product.name && p.carrier === product.carrier),
        );
      }
      if (prev.length >= 3) return [...prev.slice(1), product];
      return [...prev, product];
    });
  };

  const handleDone = () => {
    if (pending.length > 0) onDone?.(pending);
    onClose();
  };

  const uniqueCarriers = Array.from(
    new Set(products.map((p) => p.carrier)),
  ).sort();
  const uniqueTerms = Array.from(new Set(products.map((p) => p.term))).sort(
    (a, b) => parseInt(a) - parseInt(b),
  );

  const filtered = products.filter((p) => {
    const matchSearch =
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.carrier.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCarrier = filterCarrier === "all" || p.carrier === filterCarrier;
    const matchTerm = filterTerm === "all" || p.term === filterTerm;
    const matchLic =
      filterLicensing === "all" ||
      (filterLicensing === "approved" && p.licensingApproved) ||
      (filterLicensing === "pending" && !p.licensingApproved);
    return matchSearch && matchCarrier && matchTerm && matchLic;
  });

  const sorted = [...filtered].sort((a, b) => {
    switch (sortBy) {
      case "rate-desc":
        return parseFloat(b.rate) - parseFloat(a.rate);
      case "rate-asc":
        return parseFloat(a.rate) - parseFloat(b.rate);
      case "carrier":
        return a.carrier.localeCompare(b.carrier);
      case "term-asc":
        return parseInt(a.term) - parseInt(b.term);
      case "term-desc":
        return parseInt(b.term) - parseInt(a.term);
      default:
        return 0;
    }
  });

  const hasFilters =
    searchTerm ||
    filterCarrier !== "all" ||
    filterTerm !== "all" ||
    filterLicensing !== "all";

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col p-0">
        <div className="px-6 pt-6 pb-4 border-b border-slate-200">
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-2xl font-bold text-slate-900">
                Product Shelf
              </DialogTitle>
              <DialogDescription className="text-sm text-slate-600 mt-1">
                Browse and filter available products for client consideration
              </DialogDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 space-y-3">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search by product name or carrier..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 h-10 bg-white border-slate-200"
              />
            </div>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-[200px] h-10 bg-white">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="rate-desc">Rate: High to Low</SelectItem>
                <SelectItem value="rate-asc">Rate: Low to High</SelectItem>
                <SelectItem value="carrier">Carrier: A-Z</SelectItem>
                <SelectItem value="term-asc">Term: Short to Long</SelectItem>
                <SelectItem value="term-desc">Term: Long to Short</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex gap-3">
            <Select value={filterCarrier} onValueChange={setFilterCarrier}>
              <SelectTrigger className="w-[200px] h-10 bg-white">
                <SelectValue placeholder="All Carriers" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Carriers</SelectItem>
                {uniqueCarriers.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterTerm} onValueChange={setFilterTerm}>
              <SelectTrigger className="w-[180px] h-10 bg-white">
                <SelectValue placeholder="All Terms" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Terms</SelectItem>
                {uniqueTerms.map((t) => (
                  <SelectItem key={t} value={t}>
                    {t}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterLicensing} onValueChange={setFilterLicensing}>
              <SelectTrigger className="w-[200px] h-10 bg-white">
                <SelectValue placeholder="All Licensing" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Licensing Status</SelectItem>
                <SelectItem value="approved">Approved Only</SelectItem>
                <SelectItem value="pending">Pending Only</SelectItem>
              </SelectContent>
            </Select>
            {hasFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchTerm("");
                  setFilterCarrier("all");
                  setFilterTerm("all");
                  setFilterLicensing("all");
                }}
                className="h-10 text-slate-600"
              >
                Clear Filters
              </Button>
            )}
          </div>
          <div className="text-sm text-slate-600">
            Showing {sorted.length} of {products.length} products
          </div>
        </div>

        {/* Product Grid */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {sorted.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-500">
              <Search className="h-12 w-12 text-slate-300 mb-3" />
              <p className="font-medium">No products found</p>
              <p className="text-sm mt-1">Try adjusting your filters</p>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {sorted.map((product, idx) => {
                const canSell = product.licensingApproved === true;
                const isSelected = pending.some(
                  (p) =>
                    p.name === product.name && p.carrier === product.carrier,
                );
                const atMax = pending.length >= 3 && !isSelected;
                return (
                  <div
                    key={idx}
                    onClick={() => !atMax && toggleProduct(product)}
                    className={`p-4 border-2 rounded-xl transition-all ${atMax ? "opacity-50 cursor-not-allowed" : "hover:shadow-lg cursor-pointer"} ${isSelected ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200" : canSell ? "border-green-200 bg-green-50/30 hover:border-green-300" : "border-amber-200 bg-amber-50/30 hover:border-amber-300"}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-bold text-slate-900 text-sm leading-tight mb-1">
                          {product.name}
                        </h4>
                        <p className="text-xs text-slate-600">
                          {product.carrier}
                        </p>
                      </div>
                      <Button
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (!atMax) toggleProduct(product);
                        }}
                        className={`h-8 px-3 text-xs font-semibold ml-2 ${isSelected ? "bg-green-600 hover:bg-green-700 text-white" : "bg-blue-600 hover:bg-blue-700 text-white"}`}
                        disabled={atMax}
                      >
                        {isSelected ? "✓ Selected" : "Select"}
                      </Button>
                    </div>

                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                      <div className="flex items-baseline justify-between">
                        <span className="text-xs text-blue-700 font-medium">
                          Current Rate
                        </span>
                        <span className="text-2xl font-bold text-blue-900">
                          {product.rate}
                        </span>
                      </div>
                      {product.premiumBonus && (
                        <div className="mt-1 flex items-center justify-end">
                          <Gift className="h-3 w-3 text-purple-600 mr-1" />
                          <span className="text-xs text-purple-700 font-medium">
                            {product.premiumBonus} Bonus
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="space-y-2">
                      <MetricRow
                        icon={Shield}
                        color="text-green-600"
                        label="Guaranteed Min"
                        value={product.guaranteedMinRate}
                      />
                      <MetricRow
                        icon={Calendar}
                        color="text-blue-600"
                        label="Term"
                        value={product.term}
                      />
                      <MetricRow
                        icon={DollarSign}
                        color="text-emerald-600"
                        label="Free Withdrawal"
                        value={product.freeWithdrawal}
                      />
                      <MetricRow
                        icon={Zap}
                        color="text-purple-600"
                        label="Surrender Period"
                        value={`${product.surrenderPeriod} years`}
                      />
                    </div>

                    {product.riders && product.riders.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-slate-200">
                        <p className="text-xs text-slate-600 font-medium mb-1">
                          Key Features:
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {product.riders.slice(0, 2).map((r, i) => (
                            <Badge
                              key={i}
                              variant="outline"
                              className="text-xs px-1.5 py-0 bg-slate-50 text-slate-700 border-slate-300"
                            >
                              {r}
                            </Badge>
                          ))}
                          {product.riders.length > 2 && (
                            <Badge
                              variant="outline"
                              className="text-xs px-1.5 py-0 bg-slate-50 text-slate-600 border-slate-300"
                            >
                              +{product.riders.length - 2} more
                            </Badge>
                          )}
                        </div>
                      </div>
                    )}

                    {!canSell && product.licensingDetails && (
                      <div className="mt-3 pt-3 border-t border-amber-200">
                        <p className="text-xs text-amber-700 leading-relaxed">
                          {product.licensingDetails}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <p className="text-xs text-slate-600">
            {pending.length}/3 products selected
          </p>
          <Button
            onClick={handleDone}
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            Done
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function MetricRow({
  icon: Icon,
  color,
  label,
  value,
}: {
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs text-slate-600 flex items-center gap-1">
        <Icon className={`h-3.5 w-3.5 ${color}`} />
        {label}
      </span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}
