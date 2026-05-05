from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def dataframe_to_records(df: pd.DataFrame, limit: int = 100) -> list[dict[str, Any]]:
    preview = df.head(limit).replace({np.nan: None})
    return [{key: clean_value(value) for key, value in row.items()} for row in preview.to_dict("records")]


def summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()

    numeric_summary: dict[str, dict[str, float | None]] = {}
    for column in numeric_columns:
        series = pd.to_numeric(df[column], errors="coerce")
        numeric_summary[column] = {
            "ortalama": clean_value(series.mean()),
            "minimum": clean_value(series.min()),
            "maksimum": clean_value(series.max()),
            "medyan": clean_value(series.median()),
            "standart_sapma": clean_value(series.std()),
        }

    missing_by_column = {
        column: int(count)
        for column, count in df.isna().sum().sort_values(ascending=False).items()
        if int(count) > 0
    }

    return {
        "satir_sayisi": int(df.shape[0]),
        "sutun_sayisi": int(df.shape[1]),
        "eksik_veri_sayisi": int(df.isna().sum().sum()),
        "sayisal_sutunlar": numeric_columns,
        "kategorik_sutunlar": categorical_columns,
        "istatistikler": numeric_summary,
        "eksik_veriler": missing_by_column,
        "sutunlar": df.columns.tolist(),
    }


def build_dataset_context(df: pd.DataFrame, analysis: dict[str, Any] | None = None) -> str:
    analysis = analysis or summarize_dataframe(df)
    sample = dataframe_to_records(df, limit=8)
    return (
        "Veri seti ozeti:\n"
        f"- Satir sayisi: {analysis['satir_sayisi']}\n"
        f"- Sutun sayisi: {analysis['sutun_sayisi']}\n"
        f"- Eksik veri sayisi: {analysis['eksik_veri_sayisi']}\n"
        f"- Sayisal sutunlar: {', '.join(analysis['sayisal_sutunlar']) or 'Yok'}\n"
        f"- Kategorik sutunlar: {', '.join(analysis['kategorik_sutunlar']) or 'Yok'}\n"
        f"- Sayisal istatistikler: {analysis['istatistikler']}\n"
        f"- Ornek kayitlar: {sample}\n"
    )


def get_chart_data(
    df: pd.DataFrame,
    chart_type: str,
    x_column: str | None = None,
    y_column: str | None = None,
) -> dict[str, Any]:
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()

    if chart_type == "heatmap":
        corr = df[numeric_columns].corr(numeric_only=True).replace({np.nan: None}) if numeric_columns else pd.DataFrame()
        matrix = [
            {
                "x": row,
                "y": column,
                "value": clean_value(corr.loc[row, column]),
            }
            for row in corr.index
            for column in corr.columns
        ]
        return {"type": "heatmap", "columns": numeric_columns, "data": matrix}

    if not x_column:
        x_column = categorical_columns[0] if categorical_columns else (df.columns[0] if len(df.columns) else None)
    if not y_column:
        y_column = numeric_columns[0] if numeric_columns else None

    if not x_column or x_column not in df.columns:
        raise ValueError("Gecerli bir X sutunu secilmelidir.")

    if chart_type in {"bar", "line", "pie"}:
        if y_column and y_column in numeric_columns:
            grouped = df.groupby(x_column, dropna=False)[y_column].mean().reset_index().head(30)
            grouped.columns = ["name", "value"]
        else:
            grouped = df[x_column].value_counts(dropna=False).head(30).reset_index()
            grouped.columns = ["name", "value"]
        return {
            "type": chart_type,
            "x_column": x_column,
            "y_column": y_column,
            "data": dataframe_to_records(grouped, limit=30),
        }

    if chart_type == "scatter":
        if not y_column or y_column not in numeric_columns or x_column not in numeric_columns:
            raise ValueError("Scatter grafik icin iki sayisal sutun secilmelidir.")
        points = df[[x_column, y_column]].dropna().head(300)
        return {
            "type": "scatter",
            "x_column": x_column,
            "y_column": y_column,
            "data": dataframe_to_records(points, limit=300),
        }

    raise ValueError("Desteklenmeyen grafik turu.")
