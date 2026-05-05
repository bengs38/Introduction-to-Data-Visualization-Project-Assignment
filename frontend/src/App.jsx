import { Activity, BarChart3, Database, MessageSquare, Settings } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import AIReport from "./components/AIReport.jsx";
import AnomalyTable from "./components/AnomalyTable.jsx";
import ChartSuggestion from "./components/ChartSuggestion.jsx";
import ChartAIComment from "./components/ChartAIComment.jsx";
import ChatBox from "./components/ChatBox.jsx";
import DashboardCharts from "./components/DashboardCharts.jsx";
import DataTable from "./components/DataTable.jsx";
import DataCleaning from "./components/DataCleaning.jsx";
import DataQuality from "./components/DataQuality.jsx";
import FileUpload from "./components/FileUpload.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import { api, getErrorMessage } from "./utils/api.js";

export default function App() {
  const [filename, setFilename] = useState("");
  const [rows, setRows] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [chartType, setChartType] = useState("bar");
  const [xColumn, setXColumn] = useState("");
  const [yColumn, setYColumn] = useState("");
  const [chartData, setChartData] = useState(null);
  const [chartSuggestion, setChartSuggestion] = useState(null);
  const [model, setModel] = useState("llama3");
  const [report, setReport] = useState("");
  const [chartComment, setChartComment] = useState("");
  const [messages, setMessages] = useState([]);
  const [cleaningResult, setCleaningResult] = useState(null);
  const [loading, setLoading] = useState({ upload: false, chart: false, report: false, chat: false, clean: false, chartComment: false });
  const [error, setError] = useState("");

  const numericColumns = useMemo(() => analysis?.sayisal_sutunlar || [], [analysis]);
  const columns = useMemo(() => analysis?.sutunlar || [], [analysis]);

  useEffect(() => {
    if (!analysis) return;
    if (!xColumn && columns.length) setXColumn(columns[0]);
    if (!yColumn && numericColumns.length) setYColumn(numericColumns[0]);
  }, [analysis, columns, numericColumns, xColumn, yColumn]);

  useEffect(() => {
    if (analysis) refreshChart(chartType, xColumn, yColumn);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartType]);

  const setBusy = (key, value) => setLoading((current) => ({ ...current, [key]: value }));

  const warmupModel = async (selectedModel = model) => {
    try {
      await api.post("/warmup", { model: selectedModel });
    } catch {
      // Isinma istegi opsiyoneldir; Ollama kapaliysa asil AI isteginde hata gosterilir.
    }
  };

  const uploadFile = async (file) => {
    setError("");
    setBusy("upload", true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const response = await api.post("/upload", formData, { headers: { "Content-Type": "multipart/form-data" } });
      setFilename(response.data.filename);
      setRows(response.data.preview);
      setAnalysis(response.data.analysis);
      setReport("");
      setChartComment("");
      setMessages([]);
      setCleaningResult(null);
      setChartData(null);
      const firstX = response.data.analysis.sutunlar?.[0] || "";
      const firstY = response.data.analysis.sayisal_sutunlar?.[0] || "";
      setXColumn(firstX);
      setYColumn(firstY);
      await refreshChart("bar", firstX, firstY);
      await fetchChartSuggestion();
      warmupModel(model);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy("upload", false);
    }
  };

  const refreshChart = async (type = chartType, x = xColumn, y = yColumn) => {
    if (!analysis && !x) return;
    setError("");
    setBusy("chart", true);
    try {
      const response = await api.get("/charts", {
        params: { chart_type: type, x_column: x || undefined, y_column: y || undefined },
      });
      setChartData(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy("chart", false);
    }
  };

  const fetchChartSuggestion = async () => {
    try {
      const response = await api.get("/suggest-chart");
      setChartSuggestion(response.data);
    } catch {
      setChartSuggestion(null);
    }
  };

  const cleanData = async (strategy) => {
    setError("");
    setBusy("clean", true);
    try {
      const response = await api.post("/clean", { strategy });
      setRows(response.data.preview);
      setAnalysis(response.data.analysis);
      setCleaningResult(response.data.cleaning);
      setChartSuggestion(response.data.suggestion);
      setReport("");
      setChartComment("");
      setMessages([]);
      const nextX = response.data.suggestion?.x_column || response.data.analysis.sutunlar?.[0] || "";
      const nextY = response.data.suggestion?.y_column || response.data.analysis.sayisal_sutunlar?.[0] || "";
      const nextType = response.data.suggestion?.chart_type || chartType;
      setChartType(nextType);
      setXColumn(nextX);
      setYColumn(nextY);
      await refreshChart(nextType, nextX, nextY);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy("clean", false);
    }
  };

  const applyChartSuggestion = async (suggestion) => {
    const nextType = suggestion.chart_type || "bar";
    const nextX = suggestion.x_column || "";
    const nextY = suggestion.y_column || "";
    setChartType(nextType);
    setXColumn(nextX);
    setYColumn(nextY);
    await refreshChart(nextType, nextX, nextY);
  };

  const downloadReportPdf = () => {
    if (!report) return;
    const safeReport = report
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    const reportWindow = window.open("", "_blank", "width=900,height=700");
    if (!reportWindow) {
      setError("PDF penceresi acilamadi. Tarayici popup iznini kontrol edin.");
      return;
    }
    reportWindow.document.write(`
      <!doctype html>
      <html>
        <head>
          <title>AI Veri Analiz Raporu</title>
          <style>
            body { font-family: Arial, sans-serif; color: #172033; padding: 32px; line-height: 1.6; }
            h1 { color: #0f766e; margin-bottom: 4px; }
            .meta { color: #64748b; margin-bottom: 24px; }
            pre { white-space: pre-wrap; font-family: Arial, sans-serif; font-size: 13px; }
          </style>
        </head>
        <body>
          <h1>Akilli Veri Analiz Asistani</h1>
          <div class="meta">Dosya: ${filename || "Veri seti"} | Model: ${model}</div>
          <pre>${safeReport}</pre>
          <script>window.onload = () => window.print();</script>
        </body>
      </html>
    `);
    reportWindow.document.close();
  };

  const createReport = async () => {
    setError("");
    setBusy("report", true);
    try {
      const response = await api.post("/report", { model }, { timeout: 650000 });
      setReport(response.data.report);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy("report", false);
    }
  };

  const createChartComment = async () => {
    setError("");
    setBusy("chartComment", true);
    try {
      const response = await api.post("/chart-comment", {
        chart_type: chartType,
        x_column: xColumn || null,
        y_column: yColumn || null,
        model,
      });
      setChartComment(response.data.comment);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy("chartComment", false);
    }
  };

  const askQuestion = async (question) => {
    setError("");
    setMessages((current) => [...current, { role: "user", content: question }]);
    setBusy("chat", true);
    try {
      const response = await api.post("/ask", { question, model });
      setMessages((current) => [...current, { role: "assistant", content: response.data.answer }]);
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      setMessages((current) => [...current, { role: "assistant", content: message }]);
    } finally {
      setBusy("chat", false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f4f7fb]">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-line bg-ink text-white lg:block">
        <div className="flex h-16 items-center gap-3 border-b border-white/10 px-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-brand">
            <Activity size={22} />
          </div>
          <div>
            <div className="font-bold">Akıllı Veri</div>
            <div className="text-xs text-slate-300">Analiz Asistanı</div>
          </div>
        </div>
        <nav className="space-y-1 px-4 py-5 text-sm">
          {[
            ["Veri Yükleme", Database],
            ["Dashboard", BarChart3],
            ["AI Rapor", Activity],
            ["Sohbet", MessageSquare],
          ].map(([label, Icon]) => (
            <a key={label} href="#" className="flex items-center gap-3 rounded-md px-3 py-2.5 text-slate-200 hover:bg-white/10">
              <Icon size={18} />
              {label}
            </a>
          ))}
        </nav>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-line bg-white/95 backdrop-blur">
          <div className="flex min-h-16 flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between md:px-6">
            <div>
              <h1 className="text-xl font-bold text-ink">Akıllı Veri Analiz Asistanı</h1>
              <p className="text-sm text-slate-600">CSV ve Excel verileri için grafik, analiz ve yerel LLM yorumları.</p>
            </div>
            <div className="flex items-center gap-2">
              <Settings size={18} className="text-slate-500" />
              <input
                value={model}
                onChange={(event) => setModel(event.target.value)}
                onBlur={() => warmupModel(model)}
                className="w-36 rounded-md border border-line px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-teal-100"
                aria-label="Ollama model adı"
              />
            </div>
          </div>
        </header>

        <main className="space-y-5 p-4 md:p-6">
          {error ? <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">{error}</div> : null}

          <FileUpload onUpload={uploadFile} loading={loading.upload} filename={filename} />
          <SummaryCards analysis={analysis} />

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(360px,0.65fr)]">
            <DataCleaning analysis={analysis} onClean={cleanData} loading={loading.clean} result={cleaningResult} disabled={!analysis} />
            <ChartSuggestion suggestion={chartSuggestion} onApply={applyChartSuggestion} disabled={!analysis || loading.chart} />
          </div>

          <div className="grid gap-5 xl:grid-cols-[minmax(360px,0.65fr)_minmax(0,1fr)]">
            <DataQuality analysis={analysis} />
            <AnomalyTable analysis={analysis} />
          </div>

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
            <DashboardCharts
              analysis={analysis}
              chartData={chartData}
              chartType={chartType}
              setChartType={setChartType}
              xColumn={xColumn}
              setXColumn={setXColumn}
              yColumn={yColumn}
              setYColumn={setYColumn}
              onRefresh={() => refreshChart()}
              loading={loading.chart}
            />
            <AIReport report={report} onCreate={createReport} onDownloadPdf={downloadReportPdf} loading={loading.report} />
          </div>

          <ChartAIComment comment={chartComment} onCreate={createChartComment} loading={loading.chartComment} disabled={!analysis || !chartData} />

          <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
            <DataTable rows={rows} />
            <ChatBox messages={messages} onAsk={askQuestion} loading={loading.chat} />
          </div>
        </main>
      </div>
    </div>
  );
}
