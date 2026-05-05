from __future__ import annotations

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"
OLLAMA_ERROR = "Ollama çalışmıyor. Lütfen ‘ollama serve’ çalıştırın."
OLLAMA_TIMEOUT_ERROR = "Ollama yanıtı zaman aşımına uğradı. Model ilk çalıştırmada yavaş olabilir; lütfen tekrar deneyin."


def generate_with_ollama(prompt: str, model: str = DEFAULT_MODEL, num_predict: int = 300, timeout: int = 300) -> str:
    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.25,
            "top_p": 0.9,
            "num_predict": num_predict,
            "num_ctx": 2048,
            "num_thread": 4,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.Timeout as exc:
        raise RuntimeError(OLLAMA_TIMEOUT_ERROR) from exc
    except requests.RequestException as exc:
        raise RuntimeError(OLLAMA_ERROR) from exc

    data = response.json()
    return data.get("response", "").strip() or "Ollama boş bir yanıt döndürdü."


def warmup_ollama(model: str = DEFAULT_MODEL) -> None:
    generate_with_ollama("Sadece 'hazir' yaz.", model=model, num_predict=1)
