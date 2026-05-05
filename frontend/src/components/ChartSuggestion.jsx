import { Lightbulb } from "lucide-react";

const labels = {
  bar: "Bar Chart",
  line: "Line Chart",
  pie: "Pie Chart",
  scatter: "Scatter Chart",
  heatmap: "Korelasyon Heatmap",
};

export default function ChartSuggestion({ suggestion, onApply, disabled }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-3 flex items-center gap-2">
        <Lightbulb size={19} className="text-amber" />
        <h2 className="text-lg font-semibold text-ink">Otomatik Grafik Onerisi</h2>
      </div>
      {suggestion ? (
        <div className="space-y-3 text-sm text-slate-700">
          <div>
            <div className="font-semibold text-ink">{suggestion.title}</div>
            <div className="mt-1">{suggestion.reason}</div>
          </div>
          <div className="rounded-md border border-line bg-slate-50 p-3">
            <div>Grafik: {labels[suggestion.chart_type] || suggestion.chart_type}</div>
            <div>X: {suggestion.x_column || "-"}</div>
            <div>Y: {suggestion.y_column || "-"}</div>
          </div>
          <button
            type="button"
            onClick={() => onApply(suggestion)}
            disabled={disabled}
            className="w-full rounded-md bg-brand px-3 py-2 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:opacity-60"
          >
            Oneriyi Uygula
          </button>
        </div>
      ) : (
        <div className="rounded-md border border-line bg-slate-50 p-3 text-sm text-slate-600">
          Veri yuklendiginde en uygun grafik turu otomatik onerilir.
        </div>
      )}
    </section>
  );
}
