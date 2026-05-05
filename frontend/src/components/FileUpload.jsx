import { UploadCloud } from "lucide-react";

export default function FileUpload({ onUpload, loading, filename }) {
  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-ink">Dosya Yükleme</h2>
          <p className="mt-1 text-sm text-slate-600">CSV, XLS veya XLSX veri setinizi içe aktarın.</p>
        </div>
        <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-md bg-brand px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-800">
          <UploadCloud size={18} />
          <span>{loading ? "Yükleniyor" : "Dosya Seç"}</span>
          <input
            className="hidden"
            type="file"
            accept=".csv,.xlsx,.xls"
            disabled={loading}
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) onUpload(file);
              event.target.value = "";
            }}
          />
        </label>
      </div>
      {filename ? (
        <div className="mt-4 rounded-md border border-teal-200 bg-teal-50 px-3 py-2 text-sm text-teal-900">
          Aktif veri seti: <span className="font-semibold">{filename}</span>
        </div>
      ) : null}
    </section>
  );
}
