# Akilli Veri Analiz Asistani

CSV ve Excel dosyalarini analiz eden, grafiklerle gorsellestiren ve Ollama uzerinden yerel LLM ile Turkce yorumlar uretebilen modern bir veri analizi web uygulamasidir. Proje, veri gorsellestirme dersi kapsaminda React, FastAPI, pandas ve Recharts kullanilarak gelistirilmistir.

## Kisa Tanim

Kullanici bir veri dosyasi yukler. Backend dosyayi pandas ile analiz eder, frontend veriyi tablo ve grafik olarak gosterir. Kullanici isterse Ollama uzerinden AI rapor olusturabilir veya veri hakkinda sohbet alanindan soru sorabilir.

## Temel Ozellikler

- CSV, XLS ve XLSX dosyasi yukleme
- Yuklenen veriyi tablo olarak gosterme
- Satir, sutun, eksik veri ve sayisal sutun kartlari
- Ortalama, minimum, maksimum, medyan ve standart sapma hesaplama
- Bar, line, pie, scatter grafikler
- Korelasyon heatmap
- Grafik icin kullanici kontrollu sutun secimi
- Ollama destekli Turkce AI rapor
- Veri hakkinda Turkce chat alani
- Modern ve responsive dashboard arayuzu

## Mimari

```mermaid
flowchart TD
    A[Kullanici CSV veya Excel dosyasi yukler] --> B[React Frontend]
    B --> C[FastAPI Backend]

    C --> D[pandas ile veri okuma ve analiz]
    D --> E[Analiz JSON ciktilari]
    E --> B

    C --> F[Grafik verisi hazirlama]
    F --> G[Recharts grafik gosterimi]
    G --> B

    B --> H[AI Rapor veya Chat istegi]
    H --> C
    C --> I[Ollama API localhost:11434/api/generate]
    I --> J[Yerel LLM llama3]
    J --> K[Turkce yorum / rapor / cevap]
    K --> B
```

## Girdiler ve Ciktilar

### Girdiler

- Veri dosyasi: `.csv`, `.xls`, `.xlsx`
- Grafik secimleri:
  - Grafik turu: bar, line, pie, scatter, heatmap
  - X sutunu
  - Y sutunu
- Ollama model adi:
  - Varsayilan: `llama3`
  - Ornek: `llama3:latest`, `mistral`, `gemma`
- Kullanici sorusu:
  - Ornek: `Bu veride en onemli trend ne?`
  - Ornek: `Hangi kategori daha iyi performans gosteriyor?`

### Ciktilar

- Veri on izlemesi:
  - Ilk 100 kayit tablo olarak gosterilir.
- Otomatik analiz:
  - Satir sayisi
  - Sutun sayisi
  - Eksik veri sayisi
  - Sayisal sutunlar
  - Kategorik sutunlar
  - Ortalama, minimum, maksimum, medyan ve standart sapma
- Grafikler:
  - Secilen sutunlara gore Recharts ile gorsellestirme
  - Sayisal sutunlar icin korelasyon heatmap
- AI rapor:
  - Veri ozeti
  - Onemli bulgular
  - Trend analizi
  - Anomali ve eksik veri analizi
  - Riskler
  - Oneriler
  - Sonuc
- Chat cevabi:
  - Kullanici sorusuna Ollama tarafindan uretilen Turkce yanit

## Kullanilan Teknolojiler

- Frontend: React, Vite
- Stil: Tailwind CSS
- Grafikler: Recharts
- Backend: Python FastAPI
- Veri isleme: pandas, numpy, openpyxl
- LLM: Ollama API
- Baslatici: Python, keyboard, psutil

## Kurulum

### 1. Ollama

Ollama servisini baslatin:

```powershell
ollama serve
```

Varsayilan modeli indirin:

```powershell
ollama run llama3
```

### 2. Backend

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend adresi:

```text
http://localhost:8000
```

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend adresi:

```text
http://localhost:5173
```

## F8 ile Hizli Baslatma

Windows icin eklenen baslatici scripti kullanmadan once proje ana klasorunde gerekli Python paketlerini kurun:

```powershell
py -m pip install -r requirements.txt
```

Ardindan yine proje ana klasorundeyken baslaticiyi calistirin:

```powershell
py start_with_f8.py
```

Terminalde `Uygulamayi baslatmak icin F8 tusuna basin` yazisini gordukten sonra klavyeden `F8` tusuna basin.

F8'e basildiginda script:

1. Backend calismiyorsa baslatir.
2. Frontend calismiyorsa baslatir.
3. 5 saniye bekler.
4. Tarayicida `http://localhost:5173` adresini acar.

Windows'ta F8 tusu algilanmazsa VS Code'u yonetici olarak calistirmak gerekebilir.

## Ornek Veri

Projede teknoloji satis verisi iceren ornek CSV bulunur:

```text
sample_data/teknoloji_satislari.csv
```

Uygulamayi hizlica test etmek icin bu dosyayi yukleyebilirsiniz.

## API Uclari

- `POST /upload`: CSV veya Excel dosyasi yukler.
- `GET /analyze`: Yuklenen veri icin otomatik analiz dondurur.
- `GET /charts`: Secilen grafik turu ve sutunlara gore grafik verisi dondurur.
- `POST /report`: Ollama ile Turkce AI rapor uretir.
- `POST /ask`: Kullanici sorusunu veri baglami ile Ollama'ya gonderir.

## Notlar

- AI rapor ve chat ozellikleri icin Ollama servisinin calisiyor olmasi gerekir.
- `llama3` ilk calistirmada yavas yanit verebilir.
- Ollama kapaliysa uygulama su hatayi dondurur: `Ollama calismiyor. Lutfen 'ollama serve' calistirin.`
