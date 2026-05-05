import { Download, FileText, Sparkles } from "lucide-react";

export default function AIReport({ report, onCreate, onDownloadPdf, loading }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-semibold text-ink">
            <Sparkles size={19} className="text-amber" />
            AI Analiz Paneli
          </h2>
          <p className="mt-1 text-sm text-slate-600">Ollama uzerinden Turkce veri yorumu uretir.</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <button
            type="button"
            onClick={onCreate}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-md bg-coral px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#c9563d] disabled:cursor-not-allowed disabled:opacity-60"
          >
            <FileText size={18} />
            {loading ? "Rapor hazirlaniyor" : "AI Rapor Olustur"}
          </button>
          <button
            type="button"
            onClick={onDownloadPdf}
            disabled={!report}
            className="inline-flex items-center justify-center gap-2 rounded-md border border-brand px-4 py-2.5 text-sm font-semibold text-brand transition hover:bg-teal-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Download size={18} />
            PDF
          </button>
        </div>
      </div>
      <div className="min-h-48 whitespace-pre-wrap rounded-md border border-line bg-slate-50 p-4 text-sm leading-6 text-slate-700">
        {report || "Rapor olusturuldugunda veri ozeti, onemli bulgular, riskler, oneriler ve sonuc burada gosterilir."}
      </div>
    </section>
  );
}
