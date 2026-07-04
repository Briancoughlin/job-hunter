import json
import requests


DEFAULT_MODEL = "llama3.2"
DEFAULT_BASE_URL = "http://localhost:11434"


def generate_json(prompt: str, *, model: str = DEFAULT_MODEL, base_url: str = DEFAULT_BASE_URL, timeout: int = 120) -> dict:
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    content = response.json().get("response", "").strip()

    if not content:
        raise ValueError("Ollama returned an empty response")

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]

    return json.loads(content.strip())
