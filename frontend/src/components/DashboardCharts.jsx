import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Fragment } from "react";

const chartOptions = [
  { value: "bar", label: "Bar Chart" },
  { value: "line", label: "Line Chart" },
  { value: "pie", label: "Pie Chart" },
  { value: "scatter", label: "Scatter Chart" },
  { value: "heatmap", label: "Korelasyon Heatmap" },
];

const colors = ["#0f766e", "#e76f51", "#d99a2b", "#3b82f6", "#8b5cf6", "#14b8a6", "#ef4444"];

function Heatmap({ data, columns }) {
  const getCellColor = (value) => {
    if (value === null || value === undefined) return "#e5e7eb";
    const strength = Math.min(Math.abs(value), 1);
    if (value >= 0) return `rgba(15, 118, 110, ${0.18 + strength * 0.72})`;
    return `rgba(231, 111, 81, ${0.18 + strength * 0.72})`;
  };

  return (
    <div className="scrollbar-thin overflow-auto">
      <div
        className="grid min-w-[520px] gap-1"
        style={{ gridTemplateColumns: `120px repeat(${columns.length}, minmax(76px, 1fr))` }}
      >
        <div />
        {columns.map((column) => (
          <div key={column} className="truncate px-2 py-1 text-center text-xs font-semibold text-slate-600">
            {column}
          </div>
        ))}
        {columns.map((row) => (
          <Fragment key={row}>
            <div key={`${row}-label`} className="truncate px-2 py-3 text-xs font-semibold text-slate-600">
              {row}
            </div>
            {columns.map((column) => {
              const cell = data.find((item) => item.x === row && item.y === column);
              return (
                <div
                  key={`${row}-${column}`}
                  className="rounded-md px-2 py-3 text-center text-xs font-semibold text-ink"
                  style={{ background: getCellColor(cell?.value) }}
                  title={`${row} / ${column}: ${cell?.value ?? "yok"}`}
                >
                  {cell?.value === null || cell?.value === undefined ? "-" : Number(cell.value).toFixed(2)}
                </div>
              );
            })}
          </Fragment>
        ))}
      </div>
    </div>
  );
}

export default function DashboardCharts({
  analysis,
  chartData,
  chartType,
  setChartType,
  xColumn,
  setXColumn,
  yColumn,
  setYColumn,
  onRefresh,
  loading,
}) {
  const columns = analysis?.sutunlar || [];
  const numericColumns = analysis?.sayisal_sutunlar || [];

  const renderChart = () => {
    const data = chartData?.data || [];
    if (!chartData) return <div className="py-24 text-center text-sm text-slate-500">Grafik için veri bekleniyor.</div>;
    if (chartType === "heatmap") return <Heatmap data={data} columns={chartData.columns || []} />;
    if (!data.length) return <div className="py-24 text-center text-sm text-slate-500">Bu seçim için grafik verisi yok.</div>;

    if (chartType === "pie") {
      return (
        <ResponsiveContainer width="100%" height={340}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" outerRadius={112} label>
              {data.map((_, index) => (
                <Cell key={index} fill={colors[index % colors.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    if (chartType === "line") {
      return (
        <ResponsiveContainer width="100%" height={340}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d8dee8" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#0f766e" strokeWidth={3} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      );
    }

    if (chartType === "scatter") {
      return (
        <ResponsiveContainer width="100%" height={340}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" stroke="#d8dee8" />
            <XAxis dataKey={chartData.x_column} name={chartData.x_column} tick={{ fontSize: 12 }} />
            <YAxis dataKey={chartData.y_column} name={chartData.y_column} tick={{ fontSize: 12 }} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={data} fill="#e76f51" />
          </ScatterChart>
        </ResponsiveContainer>
      );
    }

    return (
      <ResponsiveContainer width="100%" height={340}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#d8dee8" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value" fill="#0f766e" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-ink">Grafikler</h2>
          <p className="mt-1 text-sm text-slate-600">Grafik türünü ve eksen sütunlarını seçin.</p>
        </div>
        <div className="grid gap-2 sm:grid-cols-4">
          <select className="rounded-md border border-line px-3 py-2 text-sm" value={chartType} onChange={(e) => setChartType(e.target.value)}>
            {chartOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <select className="rounded-md border border-line px-3 py-2 text-sm" value={xColumn} onChange={(e) => setXColumn(e.target.value)} disabled={chartType === "heatmap"}>
            <option value="">X sütunu</option>
            {(chartType === "scatter" ? numericColumns : columns).map((column) => (
              <option key={column} value={column}>
                {column}
              </option>
            ))}
          </select>
          <select className="rounded-md border border-line px-3 py-2 text-sm" value={yColumn} onChange={(e) => setYColumn(e.target.value)} disabled={chartType === "heatmap"}>
            <option value="">Y sütunu</option>
            {numericColumns.map((column) => (
              <option key={column} value={column}>
                {column}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            className="rounded-md border border-brand px-3 py-2 text-sm font-semibold text-brand transition hover:bg-teal-50 disabled:opacity-60"
          >
            {loading ? "Hazırlanıyor" : "Grafiği Güncelle"}
          </button>
        </div>
      </div>
      <div className="rounded-md border border-line bg-white p-4">{renderChart()}</div>
    </section>
  );
}
