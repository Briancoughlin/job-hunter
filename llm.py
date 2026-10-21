"""Small LLM abstraction so the app can run on Claude or a local Ollama model.

Both backends expose the same method, ``complete_json(prompt, max_tokens)``,
which returns the model's reply parsed as a JSON object.
"""

import json

import anthropic
import requests

PROVIDERS = ("Claude", "Ollama")

CLAUDE_MODEL = "claude-sonnet-4-6"
OLLAMA_DEFAULT_MODEL = "llama3.1:8b"
OLLAMA_DEFAULT_BASE_URL = "http://localhost:11434"


def parse_json(content: str) -> dict:
    content = content.strip()
    # Strip markdown code fences if present
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content.strip())


class ClaudeClient:
    name = "Claude"

    def __init__(self, api_key: str, base_url: str | None = None, model: str = CLAUDE_MODEL):
        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key, base_url=base_url or None)

    def complete_json(self, prompt: str, max_tokens: int = 1024) -> dict:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text
        print(f"[llm] claude raw response: {content[:200]}", flush=True)
        return parse_json(content)


class OllamaClient:
    name = "Ollama"

    def __init__(self, model: str = OLLAMA_DEFAULT_MODEL, base_url: str = OLLAMA_DEFAULT_BASE_URL, timeout: int = 300):
        self.model = model or OLLAMA_DEFAULT_MODEL
        self.base_url = (base_url or OLLAMA_DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout

    def complete_json(self, prompt: str, max_tokens: int = 1024) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"num_predict": max_tokens},
                },
                timeout=self.timeout,
            )
        except requests.ConnectionError as e:
            raise RuntimeError(f"Could not reach Ollama at {self.base_url}. Is Ollama running?") from e
        if response.status_code == 404:
            raise RuntimeError(f"Ollama model '{self.model}' not found. Run `ollama pull {self.model}` first.")
        response.raise_for_status()
        content = response.json().get("response", "")
        print(f"[llm] ollama raw response: {content[:200]}", flush=True)
        if not content.strip():
            raise ValueError(f"Ollama model '{self.model}' returned an empty response")
        return parse_json(content)


def make_client(
    provider: str,
    *,
    api_key: str = "",
    base_url: str = "",
    ollama_model: str = "",
    ollama_base_url: str = "",
):
    if provider == "Ollama":
        return OllamaClient(model=ollama_model, base_url=ollama_base_url)
    return ClaudeClient(api_key=api_key, base_url=base_url)
