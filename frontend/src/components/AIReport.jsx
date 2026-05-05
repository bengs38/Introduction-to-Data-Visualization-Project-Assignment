import { FileText, Sparkles } from "lucide-react";

export default function AIReport({ report, onCreate, loading }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-semibold text-ink">
            <Sparkles size={19} className="text-amber" />
            AI Analiz Paneli
          </h2>
          <p className="mt-1 text-sm text-slate-600">Ollama üzerinden Türkçe veri yorumu üretir.</p>
        </div>
        <button
          type="button"
          onClick={onCreate}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-coral px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#c9563d] disabled:cursor-not-allowed disabled:opacity-60"
        >
          <FileText size={18} />
          {loading ? "Rapor hazırlanıyor" : "AI Rapor Oluştur"}
        </button>
      </div>
      <div className="min-h-48 whitespace-pre-wrap rounded-md border border-line bg-slate-50 p-4 text-sm leading-6 text-slate-700">
        {report || "Rapor oluşturulduğunda veri özeti, önemli bulgular, riskler, öneriler ve sonuç burada gösterilir."}
      </div>
    </section>
  );
}
