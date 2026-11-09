from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CopilotIntent:
    natural_language: str
    command: str
    explanation: str
    confidence: float
    status: str = "PREVIEW_ONLY"
    executed: bool = False
    decision_created: bool = False


def _validate(payload: dict[str, Any], text: str) -> CopilotIntent:
    command = str(payload.get("command", "")).strip()
    if not command.startswith("/"):
        raise ValueError("copilot output must be a SICL command beginning with /")
    return CopilotIntent(text, command, str(payload.get("explanation", "")), float(payload.get("confidence", 0.0)))


class OllamaCopilot:
    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 20.0) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.timeout = timeout

    def translate_preview(self, text: str) -> CopilotIntent:
        if not text.strip():
            raise ValueError("natural language input is required")
        if not self.base_url:
            raise RuntimeError("COPILOT_NOT_CONFIGURED")
        body = {
            "model": self.model,
            "temperature": 0,
            "stream": False,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "Translate Spanish or English architectural requests into one SICL command. Never execute it. Return JSON only with command, explanation, confidence."},
                {"role": "user", "content": text},
            ],
        }
        request = urllib.request.Request(self.base_url + "/v1/chat/completions", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_payload = json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"COPILOT_UNAVAILABLE: {exc}") from exc
        content = response_payload["choices"][0]["message"]["content"]
        return _validate(json.loads(content), text)


def intent_to_dict(intent: CopilotIntent) -> dict[str, Any]:
    return asdict(intent)
