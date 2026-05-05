import { ShieldCheck } from "lucide-react";

export default function DataQuality({ analysis }) {
  const quality = analysis?.veri_kalite_skoru;
  const score = quality?.skor ?? 0;
  const tone = score >= 85 ? "text-teal-700" : score >= 65 ? "text-amber-700" : "text-red-700";
  const bar = score >= 85 ? "bg-brand" : score >= 65 ? "bg-amber" : "bg-coral";

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex items-center gap-2">
        <ShieldCheck size={19} className="text-brand" />
        <h2 className="text-lg font-semibold text-ink">Veri Kalite Skoru</h2>
      </div>
      {quality ? (
        <div className="space-y-4">
          <div className="flex items-end justify-between">
            <div className={`text-4xl font-bold ${tone}`}>{score}</div>
            <div className="text-sm font-semibold text-slate-600">{quality.seviye}</div>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-slate-100">
            <div className={`h-full ${bar}`} style={{ width: `${score}%` }} />
          </div>
          <div className="grid gap-2 text-sm text-slate-700">
            <div>Eksik veri orani: {quality.eksik_veri_orani}%</div>
            <div>Tekrarli satir orani: {quality.tekrarli_satir_orani}%</div>
            <div>Anomali orani: {quality.anomali_orani}%</div>
          </div>
        </div>
      ) : (
        <div className="rounded-md border border-line bg-slate-50 p-3 text-sm text-slate-600">
          Veri yuklendiginde kalite skoru hesaplanir.
        </div>
      )}
    </section>
  );
}
