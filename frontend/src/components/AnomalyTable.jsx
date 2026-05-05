import { AlertCircle } from "lucide-react";

export default function AnomalyTable({ analysis }) {
  const anomalies = analysis?.anomali_kayitlari || [];

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <AlertCircle size={19} className="text-coral" />
          <h2 className="text-lg font-semibold text-ink">Anomali Tablosu</h2>
        </div>
        <span className="rounded-md border border-line px-3 py-1 text-sm text-slate-600">{analysis?.anomali_sayisi || 0} kayit</span>
      </div>
      {anomalies.length ? (
        <div className="scrollbar-thin max-h-64 overflow-auto rounded-md border border-line">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-100 text-xs uppercase text-slate-600">
              <tr>
                <th className="px-3 py-2">Satir</th>
                <th className="px-3 py-2">Sutun</th>
                <th className="px-3 py-2">Deger</th>
                <th className="px-3 py-2">Tip</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((item, index) => (
                <tr key={`${item.satir}-${item.sutun}-${index}`} className="odd:bg-white even:bg-slate-50">
                  <td className="border-t border-slate-100 px-3 py-2">{item.satir}</td>
                  <td className="border-t border-slate-100 px-3 py-2">{item.sutun}</td>
                  <td className="border-t border-slate-100 px-3 py-2">{item.deger}</td>
                  <td className="border-t border-slate-100 px-3 py-2">{item.tip}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rounded-md border border-line bg-slate-50 p-3 text-sm text-slate-600">
          Sayisal sutunlarda IQR yontemine gore belirgin aykiri deger bulunmadi.
        </div>
      )}
    </section>
  );
}
