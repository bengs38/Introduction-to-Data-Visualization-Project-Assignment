import { Bot, Wand2 } from "lucide-react";

export default function ChartAIComment({ comment, onCreate, loading, disabled }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-semibold text-ink">
            <Bot size={19} className="text-brand" />
            Akilli Grafik Yorumu
          </h2>
          <p className="mt-1 text-sm text-slate-600">Secili grafikteki ana deseni veriye gore yorumlar.</p>
        </div>
        <button
          type="button"
          onClick={onCreate}
          disabled={disabled || loading}
          className="inline-flex items-center justify-center gap-2 rounded-md bg-brand px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Wand2 size={18} />
          {loading ? "Yorumlaniyor" : "Grafiği Yorumla"}
        </button>
      </div>
      <div className="min-h-32 whitespace-pre-wrap rounded-md border border-line bg-slate-50 p-4 text-sm leading-6 text-slate-700">
        {comment || "Grafik yorumu olusturuldugunda ana trendler ve dikkat edilmesi gereken noktalar burada gorunur."}
      </div>
    </section>
  );
}
