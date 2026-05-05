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


def detect_anomalies(df: pd.DataFrame, limit: int = 25) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

    for column in numeric_columns:
        series = pd.to_numeric(df[column], errors="coerce").dropna()
        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0 or pd.isna(iqr):
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (df[column] < lower) | (df[column] > upper)

        for index, value in df.loc[mask, column].head(limit).items():
            direction = "Yuksek" if value > upper else "Dusuk"
            anomalies.append(
                {
                    "satir": int(index) + 1,
                    "sutun": column,
                    "deger": clean_value(value),
                    "alt_sinir": clean_value(lower),
                    "ust_sinir": clean_value(upper),
                    "tip": direction,
                }
            )
            if len(anomalies) >= limit:
                return anomalies

    return anomalies


def calculate_quality_score(df: pd.DataFrame, anomalies: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    total_cells = max(int(df.shape[0] * df.shape[1]), 1)
    row_count = max(int(df.shape[0]), 1)
    missing_count = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())
    anomalies = anomalies if anomalies is not None else detect_anomalies(df)
    anomaly_count = len(anomalies)

    missing_ratio = missing_count / total_cells
    duplicate_ratio = duplicate_count / row_count
    anomaly_ratio = anomaly_count / row_count
    score = 100 - (missing_ratio * 35 + duplicate_ratio * 25 + anomaly_ratio * 40)
    score = int(max(0, min(100, round(score))))

    if score >= 85:
        label = "Yuksek"
    elif score >= 65:
        label = "Orta"
    else:
        label = "Dusuk"

    return {
        "skor": score,
        "seviye": label,
        "eksik_veri_orani": round(missing_ratio * 100, 2),
        "tekrarli_satir_orani": round(duplicate_ratio * 100, 2),
        "anomali_orani": round(anomaly_ratio * 100, 2),
        "anomali_sayisi": anomaly_count,
    }


def summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()
    anomalies = detect_anomalies(df)
    quality_score = calculate_quality_score(df, anomalies)

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
        "tekrarli_satir_sayisi": int(df.duplicated().sum()),
        "anomali_sayisi": len(anomalies),
        "anomali_kayitlari": anomalies,
        "veri_kalite_skoru": quality_score,
        "sayisal_sutunlar": numeric_columns,
        "kategorik_sutunlar": categorical_columns,
        "istatistikler": numeric_summary,
        "eksik_veriler": missing_by_column,
        "sutunlar": df.columns.tolist(),
    }


def clean_dataframe(df: pd.DataFrame, strategy: str) -> tuple[pd.DataFrame, dict[str, Any]]:
    before_rows = int(df.shape[0])
    before_missing = int(df.isna().sum().sum())
    before_duplicates = int(df.duplicated().sum())
    cleaned = df.copy()

    if strategy == "drop_missing":
        if before_missing > 0:
            cleaned = cleaned.dropna()
            action = "Eksik veri bulunan satirlar silindi."
        else:
            action = "Eksik veri bulunmadi. Silinecek satir yok."
    elif strategy == "fill_mean":
        if before_missing > 0:
            for column in cleaned.select_dtypes(include=[np.number]).columns:
                cleaned[column] = cleaned[column].fillna(cleaned[column].mean())
            for column in cleaned.select_dtypes(exclude=[np.number]).columns:
                mode = cleaned[column].mode(dropna=True)
                if not mode.empty:
                    cleaned[column] = cleaned[column].fillna(mode.iloc[0])
            action = "Eksik sayisal veriler ortalama, kategorik veriler mod ile dolduruldu."
        else:
            action = "Eksik veri bulunmadi. Doldurulacak alan yok."
    elif strategy == "drop_duplicates":
        if before_duplicates > 0:
            cleaned = cleaned.drop_duplicates()
            action = "Tekrar eden satirlar silindi."
        else:
            action = "Tekrarli satir bulunmadi. Silinecek satir yok."
    else:
        raise ValueError("Desteklenmeyen temizleme yontemi.")

    after_rows = int(cleaned.shape[0])
    after_missing = int(cleaned.isna().sum().sum())
    after_duplicates = int(cleaned.duplicated().sum())

    return cleaned, {
        "islem": action,
        "onceki_satir": before_rows,
        "sonraki_satir": after_rows,
        "silinen_satir": before_rows - after_rows,
        "onceki_eksik_veri": before_missing,
        "sonraki_eksik_veri": after_missing,
        "onceki_tekrar": before_duplicates,
        "sonraki_tekrar": after_duplicates,
    }


def suggest_chart(df: pd.DataFrame) -> dict[str, Any]:
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()

    if categorical_columns and numeric_columns:
        category = min(categorical_columns, key=lambda column: df[column].nunique(dropna=True))
        return {
            "chart_type": "bar",
            "x_column": category,
            "y_column": numeric_columns[0],
            "title": "Bar grafik onerisi",
            "reason": f"{category} kategorilerine gore {numeric_columns[0]} ortalamasini karsilastirmak icin uygun.",
        }

    if len(numeric_columns) >= 2:
        return {
            "chart_type": "scatter",
            "x_column": numeric_columns[0],
            "y_column": numeric_columns[1],
            "title": "Scatter grafik onerisi",
            "reason": "Iki sayisal sutun arasindaki iliskiyi gormek icin uygun.",
        }

    if categorical_columns:
        return {
            "chart_type": "pie",
            "x_column": categorical_columns[0],
            "y_column": None,
            "title": "Pie grafik onerisi",
            "reason": f"{categorical_columns[0]} dagilimini oran olarak gostermek icin uygun.",
        }

    return {
        "chart_type": "heatmap",
        "x_column": None,
        "y_column": None,
        "title": "Korelasyon heatmap onerisi",
        "reason": "Sayisal sutunlar arasindaki genel iliskileri incelemek icin uygun.",
    }


def build_chart_comment(chart: dict[str, Any]) -> str:
    chart_type = chart.get("type")
    data = chart.get("data", [])
    x_column = chart.get("x_column") or "X"
    y_column = chart.get("y_column") or "deger"

    if chart_type in {"bar", "pie"} and data:
        values = [item for item in data if item.get("value") is not None]
        if not values:
            return "Grafik verisinde yorumlanabilecek sayisal deger bulunmadi."
        highest = max(values, key=lambda item: item["value"])
        lowest = min(values, key=lambda item: item["value"])
        total = sum(item["value"] for item in values)
        share = (highest["value"] / total * 100) if total else 0
        return (
            f"- Grafik {x_column} kiriliminda {y_column} degerlerini karsilastiriyor.\n"
            f"- En yuksek deger {highest['name']} kategorisinde: {highest['value']:.2f}.\n"
            f"- En dusuk deger {lowest['name']} kategorisinde: {lowest['value']:.2f}.\n"
            f"- En yuksek kategori toplam/ortalama dagilimin yaklasik %{share:.1f} payini temsil ediyor.\n"
            "- Bu farkin operasyonel veya kategorik nedenleri ayrica incelenmelidir."
        )

    if chart_type == "line" and data:
        values = [item for item in data if item.get("value") is not None]
        if len(values) < 2:
            return "Line grafik icin trend yorumu yapmaya yetecek sayida nokta yok."
        first = values[0]
        last = values[-1]
        highest = max(values, key=lambda item: item["value"])
        lowest = min(values, key=lambda item: item["value"])
        change = last["value"] - first["value"]
        direction = "artis" if change > 0 else "azalis" if change < 0 else "dengeli seyir"
        return (
            f"- Grafik {x_column} boyunca {y_column} degerinin seyrini gosteriyor.\n"
            f"- Ilk nokta {first['name']} ({first['value']:.2f}), son nokta {last['name']} ({last['value']:.2f}); genel yon: {direction}.\n"
            f"- En yuksek nokta {highest['name']} ({highest['value']:.2f}), en dusuk nokta {lowest['name']} ({lowest['value']:.2f}).\n"
            "- Ani yukselis veya dusus varsa ilgili donem/kategori ayrica kontrol edilmelidir."
        )

    if chart_type == "scatter" and data:
        x_key = chart.get("x_column")
        y_key = chart.get("y_column")
        points = [(item.get(x_key), item.get(y_key)) for item in data if item.get(x_key) is not None and item.get(y_key) is not None]
        if len(points) < 3:
            return "Scatter grafik icin iliski yorumu yapmaya yetecek sayida nokta yok."
        xs = pd.Series([point[0] for point in points])
        ys = pd.Series([point[1] for point in points])
        corr = xs.corr(ys)
        if pd.isna(corr):
            relation = "belirsiz"
        elif corr >= 0.6:
            relation = "guclu pozitif"
        elif corr >= 0.3:
            relation = "orta pozitif"
        elif corr <= -0.6:
            relation = "guclu negatif"
        elif corr <= -0.3:
            relation = "orta negatif"
        else:
            relation = "zayif"
        return (
            f"- Scatter grafik {x_key} ile {y_key} arasindaki iliskiyi gosteriyor.\n"
            f"- Hesaplanan korelasyon yaklasik {corr:.2f}; iliski {relation} gorunuyor.\n"
            "- Noktalar belirli alanlarda yogunlasiyorsa segment bazli inceleme yapilabilir.\n"
            "- Uzakta kalan noktalar potansiyel anomali olarak kontrol edilmelidir."
        )

    if chart_type == "heatmap" and data:
        values = [item for item in data if item.get("value") is not None and item.get("x") != item.get("y")]
        if not values:
            return "Heatmap icin yorumlanabilecek korelasyon degeri bulunmadi."
        strongest = max(values, key=lambda item: abs(item["value"]))
        direction = "pozitif" if strongest["value"] > 0 else "negatif"
        return (
            "- Korelasyon heatmap sayisal sutunlar arasindaki iliskileri gosteriyor.\n"
            f"- En guclu iliski {strongest['x']} ile {strongest['y']} arasinda: {strongest['value']:.2f} ({direction}).\n"
            "- 1'e yakin degerler birlikte artisi, -1'e yakin degerler ters yonlu hareketi ifade eder.\n"
            "- Guclu korelasyon nedensellik anlamina gelmez; is baglami ile kontrol edilmelidir."
        )

    return "Secili grafik icin yorum uretilecek yeterli veri bulunmadi."


def build_dataset_context(df: pd.DataFrame, analysis: dict[str, Any] | None = None) -> str:
    analysis = analysis or summarize_dataframe(df)
    numeric_stats = {
        column: {
            "ortalama": stats.get("ortalama"),
            "minimum": stats.get("minimum"),
            "maksimum": stats.get("maksimum"),
        }
        for column, stats in list(analysis["istatistikler"].items())[:6]
    }

    category_summary: dict[str, dict[str, int]] = {}
    for column in analysis["kategorik_sutunlar"][:3]:
        counts = df[column].value_counts(dropna=False).head(5)
        category_summary[column] = {str(key): int(value) for key, value in counts.items()}

    anomaly_sample = [
        {
            "satir": item["satir"],
            "sutun": item["sutun"],
            "deger": item["deger"],
            "tip": item["tip"],
        }
        for item in analysis["anomali_kayitlari"][:10]
    ]

    return (
        "Veri seti ozeti:\n"
        f"- Satir sayisi: {analysis['satir_sayisi']}\n"
        f"- Sutun sayisi: {analysis['sutun_sayisi']}\n"
        f"- Eksik veri sayisi: {analysis['eksik_veri_sayisi']}\n"
        f"- Tekrarli satir sayisi: {analysis['tekrarli_satir_sayisi']}\n"
        f"- Anomali sayisi: {analysis['anomali_sayisi']}\n"
        f"- Veri kalite skoru: {analysis['veri_kalite_skoru']['skor']} ({analysis['veri_kalite_skoru']['seviye']})\n"
        f"- Sayisal sutunlar: {', '.join(analysis['sayisal_sutunlar']) or 'Yok'}\n"
        f"- Kategorik sutunlar: {', '.join(analysis['kategorik_sutunlar']) or 'Yok'}\n"
        f"- Sayisal istatistikler: {numeric_stats}\n"
        f"- Kategori dagilimlari: {category_summary}\n"
        f"- Eksik veri dagilimi: {analysis['eksik_veriler']}\n"
        f"- Ilk anomali kayitlari: {anomaly_sample}\n"
    )


def build_anomaly_answer(analysis: dict[str, Any]) -> str:
    anomalies = analysis.get("anomali_kayitlari", [])
    count = analysis.get("anomali_sayisi", 0)
    if count == 0:
        return "Bu veri setinde IQR yontemine gore anomali bulunmuyor."

    lines = [f"Bu veri setinde IQR yontemine gore {count} anomali var."]
    for item in anomalies[:10]:
        lines.append(
            f"- Satir {item['satir']}: {item['sutun']} = {item['deger']} ({item['tip']}, normal aralik: {item['alt_sinir']:.2f} - {item['ust_sinir']:.2f})"
        )
    if count > 10:
        lines.append(f"- Ilk 10 kayit gosterildi; toplam anomali sayisi {count}.")
    return "\n".join(lines)


def build_deterministic_report(analysis: dict[str, Any]) -> str:
    quality = analysis["veri_kalite_skoru"]
    stats = analysis["istatistikler"]
    top_numeric = list(stats.items())[:5]
    missing_text = (
        ", ".join(f"{column}: {count}" for column, count in analysis["eksik_veriler"].items())
        if analysis["eksik_veriler"]
        else "Eksik veri bulunmuyor."
    )
    anomaly_lines = [
        f"- Satir {item['satir']}: {item['sutun']} = {item['deger']} ({item['tip']})"
        for item in analysis["anomali_kayitlari"][:8]
    ]
    anomaly_text = "\n".join(anomaly_lines) if anomaly_lines else "- IQR yontemine gore belirgin anomali bulunmuyor."
    stats_text = "\n".join(
        f"- {column}: ortalama {values['ortalama']}, min {values['minimum']}, max {values['maksimum']}"
        for column, values in top_numeric
    ) or "- Sayisal sutun bulunmuyor."

    return (
        "AI Veri Analiz Raporu\n\n"
        "1. Veri Ozeti\n"
        f"- Veri seti {analysis['satir_sayisi']} satir ve {analysis['sutun_sayisi']} sutundan olusuyor.\n"
        f"- Sayisal sutun sayisi {len(analysis['sayisal_sutunlar'])}, kategorik sutun sayisi {len(analysis['kategorik_sutunlar'])}.\n"
        f"- Veri kalite skoru {quality['skor']} / 100 ({quality['seviye']}).\n\n"
        "2. Onemli Bulgular\n"
        f"{stats_text}\n\n"
        "3. Trend Analizi\n"
        "- Sayisal sutunlardaki minimum, maksimum ve ortalama degerler genel egilimi incelemek icin kullanilabilir.\n"
        "- Grafik alanindaki otomatik oneriler kategori bazli karsilastirmayi destekler.\n"
        "- Daha guclu trend yorumu icin zaman veya sirali kategori sutunu secilmelidir.\n\n"
        "4. Anomali ve Eksik Veri Analizi\n"
        f"- Eksik veri sayisi: {analysis['eksik_veri_sayisi']}.\n"
        f"- Eksik veri dagilimi: {missing_text}\n"
        f"- Anomali sayisi: {analysis['anomali_sayisi']}.\n"
        f"{anomaly_text}\n\n"
        "5. Riskler\n"
        "- Eksik veriler analiz sonuclarinda sapmaya neden olabilir.\n"
        "- Anomali degerler ortalama ve grafik yorumlarini etkileyebilir.\n"
        "- Tekrarli satirlar varsa toplam veya ortalama hesaplari sisme riski tasir.\n\n"
        "6. Oneriler\n"
        "- Eksik veriler icin uygun temizleme yontemi uygulanmali.\n"
        "- Anomali tablosundaki satirlar kaynak veriyle kontrol edilmeli.\n"
        "- Grafikler farkli X/Y sutunlariyla tekrar denenerek veri daha kapsamli incelenmeli.\n\n"
        "7. Sonuc\n"
        "- Veri seti genel olarak dashboard uzerinden analiz edilebilir durumdadir.\n"
        "- Kalite skoru, anomali tablosu ve grafikler birlikte degerlendirilerek daha guvenilir yorum yapilabilir."
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
