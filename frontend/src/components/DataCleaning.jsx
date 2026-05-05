import { Eraser, RefreshCw } from "lucide-react";

const strategies = [
  { value: "fill_mean", label: "Eksikleri Doldur", needs: "missing" },
  { value: "drop_missing", label: "Eksik Satirlari Sil", needs: "missing" },
  { value: "drop_duplicates", label: "Tekrarlari Sil", needs: "duplicates" },
];

export default function DataCleaning({ analysis, onClean, loading, result, disabled }) {
  const missingCount = analysis?.eksik_veri_sayisi || 0;
  const duplicateCount = analysis?.tekrarli_satir_sayisi || 0;
  const isStrategyDisabled = (strategy) => {
    if (disabled || loading) return true;
    if (strategy.needs === "missing") return missingCount === 0;
    if (strategy.needs === "duplicates") return duplicateCount === 0;
    return false;
  };

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex items-center gap-2">
        <Eraser size={19} className="text-brand" />
        <h2 className="text-lg font-semibold text-ink">Veri Temizleme</h2>
      </div>
      <div className="grid gap-2 sm:grid-cols-3">
        {strategies.map((strategy) => (
          <button
            key={strategy.value}
            type="button"
            onClick={() => onClean(strategy.value)}
            disabled={isStrategyDisabled(strategy)}
            title={isStrategyDisabled(strategy) && !disabled ? "Bu islem icin gerekli veri problemi yok." : strategy.label}
            className="inline-flex items-center justify-center gap-2 rounded-md border border-line px-3 py-2 text-sm font-semibold text-slate-700 transition hover:border-brand hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw size={16} />
            {strategy.label}
          </button>
        ))}
      </div>
      <div className="mt-4 rounded-md border border-line bg-slate-50 p-3 text-sm text-slate-700">
        {result ? (
          <div className="space-y-1">
            <div className="font-semibold text-ink">{result.islem}</div>
            <div>Satir: {result.onceki_satir} -&gt; {result.sonraki_satir}</div>
            <div>Eksik veri: {result.onceki_eksik_veri} -&gt; {result.sonraki_eksik_veri}</div>
            <div>Tekrarli satir: {result.onceki_tekrar} -&gt; {result.sonraki_tekrar}</div>
          </div>
        ) : (
          missingCount === 0 && duplicateCount === 0
            ? "Bu veri setinde eksik veri veya tekrarli satir gorunmuyor. Temizleme islemi gerekmiyor."
            : "Eksik veri doldurma, eksik satirlari silme veya tekrar eden satirlari kaldirma islemi uygulanabilir."
        )}
      </div>
    </section>
  );
}
