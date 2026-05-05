from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_analyzer import build_dataset_context, dataframe_to_records, get_chart_data, summarize_dataframe
from ollama_service import DEFAULT_MODEL, generate_with_ollama


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
DATA_FILE = DATA_DIR / "current_dataset.pkl"


class AskRequest(BaseModel):
    question: str
    model: str = DEFAULT_MODEL


class ReportRequest(BaseModel):
    model: str = DEFAULT_MODEL


def require_dataframe() -> pd.DataFrame:
    global CURRENT_DF
    if CURRENT_DF is None:
        if DATA_FILE.exists():
            CURRENT_DF = pd.read_pickle(DATA_FILE)
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


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, Any]:
    global CURRENT_DF, CURRENT_FILENAME

    content = await file.read()
    df = read_uploaded_file(file, content)
    CURRENT_DF = df
    CURRENT_FILENAME = file.filename
    DATA_DIR.mkdir(exist_ok=True)
    df.to_pickle(DATA_FILE)

    return {
        "message": "Dosya başarıyla yüklendi.",
        "filename": CURRENT_FILENAME,
        "columns": df.columns.tolist(),
        "preview": dataframe_to_records(df, limit=100),
        "analysis": summarize_dataframe(df),
    }


@app.get("/analyze")
def analyze() -> dict[str, Any]:
    df = require_dataframe()
    return summarize_dataframe(df)


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
    context = build_dataset_context(df)
    prompt = (
        "Sen Türkçe konuşan profesyonel bir veri analizi asistanısın. "
        "Yanıtını açık, kısa ve veri odaklı ver. Emin olmadığın noktaları belirt.\n\n"
        f"{context}\n"
        f"Kullanıcı sorusu: {request.question}\n\n"
        "Türkçe cevap:"
    )
    try:
        answer = generate_with_ollama(prompt, request.model)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"answer": answer}


@app.post("/report")
def report(request: ReportRequest) -> dict[str, str]:
    df = require_dataframe()
    analysis = summarize_dataframe(df)
    context = build_dataset_context(df, analysis)
    prompt = (
        "Sen üst düzey bir veri analisti gibi davran. Aşağıdaki veri seti için Türkçe, "
        "profesyonel ve ders projesine uygun bir AI raporu hazırla.\n\n"
        f"{context}\n"
        "Rapor şu başlıkları içersin:\n"
        "1. Veri Özeti\n"
        "2. Önemli Bulgular\n"
        "3. Trend Analizi\n"
        "4. Anomali ve Eksik Veri Analizi\n"
        "5. Riskler\n"
        "6. Öneriler\n"
        "7. Sonuç\n"
    )
    try:
        result = generate_with_ollama(prompt, request.model)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"report": result}
