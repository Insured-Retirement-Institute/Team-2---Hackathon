import { useState, useEffect } from "react";
import type { VisualizationProduct } from "@/types/alert-detail";
import { TrendingUp, Zap, DollarSign } from "lucide-react";
import {
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  BarChart,
  Bar,
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"];

interface Props {
  products: VisualizationProduct[];
}

export function InteractiveComparisonCharts({ products }: Props) {
  const [selected, setSelected] = useState<string[]>(
    products.slice(0, 4).map((p) => p.id),
  );
  const [chartMode, setChartMode] = useState<"value" | "rates">("value");

  // Sync selection when products change (e.g. shelf swap)
  useEffect(() => {
    const validIds = new Set(products.map((p) => p.id));
    setSelected((prev) => {
      const filtered = prev.filter((id) => validIds.has(id));
      return filtered.length > 0
        ? filtered
        : products.slice(0, 4).map((p) => p.id);
    });
  }, [products]);

  const toggle = (id: string) => {
    if (selected.includes(id)) {
      if (selected.length > 1) setSelected(selected.filter((s) => s !== id));
    } else if (selected.length < 4) {
      setSelected([...selected, id]);
    }
  };

  const getColor = (id: string) =>
    COLORS[products.findIndex((p) => p.id === id) % COLORS.length];

  // Filter to only valid selected IDs
  const validSelected = selected.filter((id) =>
    products.some((p) => p.id === id),
  );

  // Build chart data
  const perfData = Array.from({ length: 21 }, (_, i) => {
    const pt: Record<string, number> = { year: i };
    validSelected.forEach((id) => {
      const p = products.find((x) => x.id === id);
      if (!p) return;
      const d = p.performanceData.find((x) => x.year === i);
      if (d) pt[`${p.name}_value`] = d.value;
    });
    return pt;
  });

  const rateData = Array.from({ length: 11 }, (_, i) => {
    const pt: Record<string, number> = { year: i };
    validSelected.forEach((id) => {
      const p = products.find((x) => x.id === id);
      if (!p) return;
      const d = p.projectedRates.find((x) => x.year === i);
      if (d) pt[`${p.name}_expected`] = d.expectedRate;
    });
    return pt;
  });

  const selectedProducts = validSelected
    .map((id) => products.find((p) => p.id === id))
    .filter(Boolean) as typeof products;

  // Income milestones for bar chart
  const milestones = [10, 15, 20];
  const incomeData = milestones.map((yr) => {
    const row: Record<string, string | number> = { milestone: `Year ${yr}` };
    selectedProducts.forEach((p) => {
      const d = p.performanceData.find((x) => x.year === yr);
      row[p.name] = d?.income ?? 0;
    });
    return row;
  });

  return (
    <div className="space-y-6">
      {/* Product selector */}
      <div className="border border-slate-200 rounded-xl p-5 bg-white">
        <h3 className="text-lg font-bold text-slate-900 mb-1">
          Interactive Product Comparison
        </h3>
        <p className="text-sm text-slate-600 mb-4">
          Select up to 4 products to compare
        </p>
        <div className="flex flex-wrap gap-2">
          {products.map((p) => {
            const sel = selected.includes(p.id);
            const color = getColor(p.id);
            return (
              <button
                key={p.id}
                onClick={() => toggle(p.id)}
                className={`px-4 py-2 rounded-lg border-2 text-sm font-medium transition-all ${sel ? "shadow-md" : "border-slate-200 hover:border-slate-300 bg-white text-slate-700"}`}
                style={
                  sel
                    ? {
                        borderColor: color,
                        backgroundColor: `${color}15`,
                        color,
                      }
                    : {}
                }
              >
                <div className="flex items-center gap-2">
                  {sel && (
                    <div
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                  )}
                  <span>{p.name}</span>
                  <span className="text-xs opacity-70">({p.carrier})</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Combined Chart */}
      <div className="border border-slate-200 rounded-xl p-6 bg-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <div>
              <h3 className="font-bold text-slate-900">
                {chartMode === "value"
                  ? "Account Value Projections"
                  : "Interest Rate Projections"}
              </h3>
              <p className="text-sm text-slate-600">
                {chartMode === "value"
                  ? "Projected account values over 20 years"
                  : "Expected rate scenarios for the first 10 years"}
              </p>
            </div>
          </div>
          <div className="flex items-center bg-slate-100 rounded-lg p-1">
            <button
              onClick={() => setChartMode("value")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${chartMode === "value" ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"}`}
            >
              Account Value
            </button>
            <button
              onClick={() => setChartMode("rates")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${chartMode === "rates" ? "bg-white text-blue-700 shadow-sm" : "text-slate-600 hover:text-slate-900"}`}
            >
              % Interest Rates
            </button>
          </div>
        </div>

        {chartMode === "value" ? (
          <ResponsiveContainer width="100%" height={380}>
            <ComposedChart data={perfData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="year"
                stroke="#64748b"
                label={{ value: "Years", position: "insideBottom", offset: -5 }}
              />
              <YAxis
                stroke="#64748b"
                tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
              />
              <RechartsTooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "2px solid #cbd5e1",
                  borderRadius: 8,
                }}
                formatter={(value: unknown, name?: string) => [
                  `$${Number(value).toLocaleString()}`,
                  (name ?? "").replace("_value", ""),
                ]}
              />
              <Legend formatter={(v: string) => v.replace("_value", "")} />
              {selectedProducts.map((p) => (
                <Line
                  key={p.id}
                  type="monotone"
                  dataKey={`${p.name}_value`}
                  name={`${p.name}_value`}
                  stroke={getColor(p.id)}
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={380}>
            <AreaChart data={rateData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="year"
                stroke="#64748b"
                label={{ value: "Year", position: "insideBottom", offset: -5 }}
              />
              <YAxis stroke="#64748b" tickFormatter={(v) => `${v}%`} />
              <RechartsTooltip
                formatter={(v: unknown) => `${Number(v).toFixed(2)}%`}
                contentStyle={{
                  backgroundColor: "white",
                  border: "2px solid #cbd5e1",
                  borderRadius: 8,
                }}
              />
              <Legend formatter={(v: string) => v.replace("_expected", "")} />
              {selectedProducts.map((p) => (
                <Area
                  key={p.id}
                  type="monotone"
                  dataKey={`${p.name}_expected`}
                  name={`${p.name}_expected`}
                  stroke={getColor(p.id)}
                  fill={getColor(p.id)}
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Guaranteed Annual Income Comparison */}
      <div className="border border-slate-200 rounded-xl p-6 bg-white">
        <div className="flex items-center gap-2 mb-1">
          <DollarSign className="h-5 w-5 text-emerald-600" />
          <h3 className="font-bold text-slate-900">
            Guaranteed Annual Income Comparison
          </h3>
        </div>
        <p className="text-sm text-slate-600 mb-4">
          Projected annual income at key milestones (4.5% withdrawal rate)
        </p>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={incomeData} barCategoryGap="20%">
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e2e8f0"
              vertical={false}
            />
            <XAxis dataKey="milestone" stroke="#64748b" />
            <YAxis
              stroke="#64748b"
              tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
            />
            <RechartsTooltip
              contentStyle={{
                backgroundColor: "white",
                border: "2px solid #cbd5e1",
                borderRadius: 8,
              }}
              formatter={(value: unknown, name?: string) => [
                `$${Number(value).toLocaleString()}`,
                name ?? "",
              ]}
            />
            <Legend />
            {selectedProducts.map((p) => (
              <Bar
                key={p.id}
                dataKey={p.name}
                name={p.name}
                fill={getColor(p.id)}
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Comparison Insights */}
      <div className="border border-slate-200 rounded-xl p-6 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="flex items-start gap-3">
          <div className="h-10 w-10 rounded-lg bg-blue-600 flex items-center justify-center shrink-0">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 mb-2">
              Comparison Insights
            </h3>
            <div className="space-y-2 text-sm text-slate-700">
              <p>
                <span className="font-semibold">Rate Range:</span>{" "}
                {Math.min(
                  ...selectedProducts.map((p) => p.currentRate),
                ).toFixed(2)}
                % –{" "}
                {Math.max(
                  ...selectedProducts.map((p) => p.currentRate),
                ).toFixed(2)}
                % current rates
              </p>
              <p>
                <span className="font-semibold">Surrender Periods:</span>{" "}
                {selectedProducts
                  .map((p) => `${p.name} (${p.surrenderYears} yrs)`)
                  .join(", ")}
              </p>
              <p>
                <span className="font-semibold">20-Year Projected Value:</span>{" "}
                {selectedProducts
                  .map((p) => {
                    const last =
                      p.performanceData[p.performanceData.length - 1];
                    return `${p.name} ($${last?.value.toLocaleString()})`;
                  })
                  .join(", ")}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
