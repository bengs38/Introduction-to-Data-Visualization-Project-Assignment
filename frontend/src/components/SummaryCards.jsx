import { AlertTriangle, Hash, LayoutGrid, Sigma } from "lucide-react";

const cards = [
  { key: "satir_sayisi", label: "Satır", icon: Hash },
  { key: "sutun_sayisi", label: "Sütun", icon: LayoutGrid },
  { key: "eksik_veri_sayisi", label: "Eksik Veri", icon: AlertTriangle },
  { key: "numeric", label: "Sayısal Sütun", icon: Sigma },
];

export default function SummaryCards({ analysis }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map(({ key, label, icon: Icon }) => {
        const value = key === "numeric" ? analysis?.sayisal_sutunlar?.length || 0 : analysis?.[key] || 0;
        return (
          <div key={key} className="rounded-lg border border-line bg-panel p-4 shadow-soft">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-600">{label}</span>
              <Icon className="text-brand" size={20} />
            </div>
            <div className="mt-3 text-3xl font-bold text-ink">{value}</div>
          </div>
        );
      })}
    </div>
  );
}
