from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_analyzer import build_anomaly_answer, build_chart_comment, build_deterministic_report, clean_dataframe, build_dataset_context, dataframe_to_records, get_chart_data, summarize_dataframe, suggest_chart
from ollama_service import DEFAULT_MODEL, generate_with_ollama, warmup_ollama


app = FastAPI(title="Akıllı Veri Analiz Asistanı", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURRENT_DF: Optional[pd.DataFrame] = None
CURRENT_FILENAME: Optional[str] = None
DATA_DIR = Path(__file__).resolve().parent / ".runtime_data"
DATA_FILE = DATA_DIR / "current_dataset.csv"


class AskRequest(BaseModel):
    question: str
    model: str = DEFAULT_MODEL


class ReportRequest(BaseModel):
    model: str = DEFAULT_MODEL


class WarmupRequest(BaseModel):
    model: str = DEFAULT_MODEL


class CleanRequest(BaseModel):
    strategy: str


class ChartCommentRequest(BaseModel):
    chart_type: str
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    model: str = DEFAULT_MODEL


def require_dataframe() -> pd.DataFrame:
    global CURRENT_DF
    if CURRENT_DF is None:
        if DATA_FILE.exists():
            CURRENT_DF = pd.read_csv(DATA_FILE)
        else:
            raise HTTPException(status_code=400, detail="Önce CSV veya Excel dosyası yükleyin.")
    return CURRENT_DF


def read_uploaded_file(file: UploadFile, content: bytes) -> pd.DataFrame:
    filename = (file.filename or "").lower()
    try:
        if filename.endswith(".csv"):
            try:
                return pd.read_csv(BytesIO(content))
            except UnicodeDecodeError:
                return pd.read_csv(BytesIO(content), encoding="latin-1")
        if filename.endswith((".xlsx", ".xls")):
            return pd.read_excel(BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Dosya okunamadı: {exc}") from exc

    raise HTTPException(status_code=400, detail="Sadece CSV, XLS ve XLSX dosyaları desteklenir.")


@app.get("/")
def health() -> dict[str, str]:
    return {"durum": "çalışıyor", "uygulama": "Akıllı Veri Analiz Asistanı"}


@app.post("/warmup")
def warmup(request: WarmupRequest) -> dict[str, str]:
    try:
        warmup_ollama(request.model)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"message": "Model hazır."}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, Any]:
    global CURRENT_DF, CURRENT_FILENAME

    content = await file.read()
    df = read_uploaded_file(file, content)
    CURRENT_DF = df
    CURRENT_FILENAME = file.filename
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(DATA_FILE, index=False)

    return {
        "message": "Dosya başarıyla yüklendi.",
        "filename": CURRENT_FILENAME,
        "columns": df.columns.tolist(),
        "preview": dataframe_to_records(df, limit=500),
        "analysis": summarize_dataframe(df),
    }


@app.get("/analyze")
def analyze() -> dict[str, Any]:
    df = require_dataframe()
    return summarize_dataframe(df)


@app.get("/suggest-chart")
def suggested_chart() -> dict[str, Any]:
    df = require_dataframe()
    return suggest_chart(df)


@app.post("/clean")
def clean_data(request: CleanRequest) -> dict[str, Any]:
    global CURRENT_DF
    df = require_dataframe()
    try:
        cleaned, summary = clean_dataframe(df, request.strategy)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    CURRENT_DF = cleaned
    DATA_DIR.mkdir(exist_ok=True)
    cleaned.to_csv(DATA_FILE, index=False)

    return {
        "message": summary["islem"],
        "cleaning": summary,
        "preview": dataframe_to_records(cleaned, limit=500),
        "analysis": summarize_dataframe(cleaned),
        "suggestion": suggest_chart(cleaned),
    }


@app.get("/charts")
def charts(
    chart_type: str = Query("bar", pattern="^(bar|line|pie|scatter|heatmap)$"),
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
) -> dict[str, Any]:
    df = require_dataframe()
    try:
        return get_chart_data(df, chart_type, x_column, y_column)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/ask")
def ask(request: AskRequest) -> dict[str, str]:
    df = require_dataframe()
    analysis = summarize_dataframe(df)
    question_lower = request.question.lower()
    if "anomali" in question_lower or "aykırı" in question_lower or "aykiri" in question_lower:
        return {"answer": build_anomaly_answer(analysis)}

    context = build_dataset_context(df, analysis)
    prompt = (
        "Sen Turkce konusan profesyonel bir veri analizi asistanisin. "
        "Yaniti 3-5 maddeyle, kisa ve veri odakli ver. Uydurma bilgi verme. "
        "Verilen sayisal metrikleri aynen kullan; anomali, eksik veri veya kalite skoru sayilarini degistirme.\n\n"
        f"{context}\n"
        f"Kullanici sorusu: {request.question}\n\n"
        "Turkce kisa cevap:"
    )
    try:
        answer = generate_with_ollama(prompt, request.model, num_predict=160)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"answer": answer}


@app.post("/report")
def report(request: ReportRequest) -> dict[str, str]:
    df = require_dataframe()
    analysis = summarize_dataframe(df)
    context = build_dataset_context(df, analysis)
    prompt = (
        "Sen profesyonel bir veri analistisin. Asagidaki veri seti icin Turkce, ayrintili "
        "ama okunabilir bir AI raporu hazirla. Her baslik altinda 3-5 madde kullan.\n\n"
        f"{context}\n"
        "Rapor su basliklari icersin:\n"
        "1. Veri Ozeti\n"
        "2. Onemli Bulgular\n"
        "3. Trend Analizi\n"
        "4. Anomali ve Eksik Veri Analizi\n"
        "5. Riskler\n"
        "6. Oneriler\n"
        "7. Sonuc\n"
    )
    try:
        result = generate_with_ollama(prompt, request.model, num_predict=750, timeout=600)
    except RuntimeError as exc:
        fallback = build_deterministic_report(analysis)
        result = (
            "Not: Ollama raporu zamaninda tamamlayamadi veya hata verdi. "
            "Asagidaki rapor backend tarafinda hesaplanan kesin analiz sonuclarindan olusturuldu.\n\n"
            f"{fallback}"
        )
    return {"report": result}


@app.post("/chart-comment")
def chart_comment(request: ChartCommentRequest) -> dict[str, str]:
    df = require_dataframe()
    try:
        chart = get_chart_data(df, request.chart_type, request.x_column, request.y_column)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"comment": build_chart_comment(chart)}
