from __future__ import annotations

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"
OLLAMA_ERROR = "Ollama çalışmıyor. Lütfen ‘ollama serve’ çalıştırın."
OLLAMA_TIMEOUT_ERROR = "Ollama yanıtı zaman aşımına uğradı. Model ilk çalıştırmada yavaş olabilir; lütfen tekrar deneyin."


def generate_with_ollama(prompt: str, model: str = DEFAULT_MODEL) -> str:
    payload = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.25,
            "top_p": 0.9,
            "num_predict": 700,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)
        response.raise_for_status()
    except requests.Timeout as exc:
        raise RuntimeError(OLLAMA_TIMEOUT_ERROR) from exc
    except requests.RequestException as exc:
        raise RuntimeError(OLLAMA_ERROR) from exc

    data = response.json()
    return data.get("response", "").strip() or "Ollama boş bir yanıt döndürdü."
