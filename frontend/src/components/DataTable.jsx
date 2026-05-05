export default function DataTable({ rows }) {
  const columns = rows?.length ? Object.keys(rows[0]) : [];

  return (
    <section className="rounded-lg border border-line bg-panel p-5 shadow-soft">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink">Veri Tablosu</h2>
          <p className="mt-1 text-sm text-slate-600">Ilk 500 kayit gosterilir.</p>
        </div>
        <span className="rounded-md border border-line px-3 py-1 text-sm text-slate-600">{rows?.length || 0} kayit</span>
      </div>
      <div className="scrollbar-thin max-h-[420px] overflow-auto rounded-md border border-line">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="sticky top-0 bg-slate-100 text-xs uppercase tracking-wide text-slate-600">
            <tr>
              {columns.map((column) => (
                <th key={column} className="whitespace-nowrap border-b border-line px-3 py-3 font-semibold">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows?.length ? (
              rows.map((row, index) => (
                <tr key={index} className="odd:bg-white even:bg-slate-50">
                  {columns.map((column) => (
                    <td key={column} className="whitespace-nowrap border-b border-slate-100 px-3 py-2 text-slate-700">
                      {row[column] === null || row[column] === undefined ? "-" : String(row[column])}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-3 py-8 text-center text-slate-500">Henuz veri yuklenmedi.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
