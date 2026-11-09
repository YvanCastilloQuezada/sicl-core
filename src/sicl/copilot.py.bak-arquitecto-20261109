"""
Copiloto SICL: traduce lenguaje natural a comandos del catálogo.

NO ejecuta. NO crea decisiones. Solo sugiere el comando SICL más
apropiado del catálogo real (100 comandos en commands-catalog.json).

Si no hay match, devuelve command="UNKNOWN" con confidence=0 y
status="NO_MATCH". El cliente debe tratarlo como "el copiloto no
encontró comando", no como error.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any

from .command_catalog import catalog_for_prompt, is_known_command


@dataclass(frozen=True)
class CopilotIntent:
    natural_language: str
    command: str
    explanation: str
    confidence: float
    status: str = "PREVIEW_ONLY"  # PREVIEW_ONLY | NO_MATCH | NEEDS_REVIEW
    executed: bool = False
    decision_created: bool = False


_SYSTEM_PROMPT = (
    "Eres un copiloto de ARKI/SICL. Tu única tarea es traducir solicitudes "
    "de arquitectura (en español o inglés) a UN comando SICL del catálogo "
    "proporcionado abajo.\n\n"
    "REGLAS ESTRICTAS:\n"
    "1. Devuelve SOLO JSON con las claves: command, explanation, confidence.\n"
    "2. `command` DEBE empezar con '/' y corresponder a un comando del catálogo.\n"
    "3. Si NINGÚN comando del catálogo puede satisfacer la solicitud, "
    "devuelve command=\"UNKNOWN\", confidence=0.0, explanation=\"No hay "
    "comando SICL para esta solicitud.\"\n"
    "4. NO inventes comandos. NO ejecutes nada. NUNCA inventes.\n"
    "5. `confidence` es un número entre 0.0 y 1.0.\n\n"
    "CATÁLOGO DE COMANDOS SICL DISPONIBLES:\n"
    "{catalog}\n\n"
    "EJEMPLOS:\n"
    "Solicitud: \"crea un proyecto llamado UPAO-001\"\n"
    "Comando: \"/PROJECT CREATE UPAO-001 \\\"UPAO\\\"\"\n"
    "Confidence: 0.95\n\n"
    "Solicitud: \"registra el hecho: el FAR es 5\"\n"
    "Comando: \"/FACT SET \\\"el FAR es 5\\\" <source>\"\n"
    "Confidence: 0.9\n\n"
    "Solicitud: \"abre el proyecto UPAO-001\"\n"
    "Comando: \"/PROJECT OPEN UPAO-001\"\n"
    "Confidence: 0.98\n\n"
    "Solicitud: \"crea una pared de 5 metros\"\n"
    "Comando: \"UNKNOWN\"\n"
    "Confidence: 0.0\n"
    "Explanation: \"No hay comando SICL para crear paredes. "
    "Los comandos SICL gestionan proyectos, decisiones y conocimiento, "
    "no geometría directa.\"\n"
)


def _validate(payload: dict[str, Any], text: str) -> CopilotIntent:
    command = str(payload.get("command", "")).strip()
    explanation = str(payload.get("explanation", "")).strip()
    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    # acotar
    confidence = max(0.0, min(1.0, confidence))

    if not command:
        raise ValueError("copilot output must include 'command'")

    # Caso UNKNOWN: el modelo admite que no hay match. NO es error.
    if command.upper() == "UNKNOWN":
        return CopilotIntent(
            natural_language=text,
            command="UNKNOWN",
            explanation=explanation or "No SICL command matches this request.",
            confidence=0.0,
            status="NO_MATCH",
        )

    # Debe empezar con /
    if not command.startswith("/"):
        raise ValueError("copilot output must be a SICL command beginning with /")

    # Debe pertenecer al catálogo
    if not is_known_command(command):
        # El modelo inventó un comando. No lo aceptamos como PREVIEW_ONLY.
        return CopilotIntent(
            natural_language=text,
            command="UNKNOWN",
            explanation=(
                f"El comando '{command}' no existe en el catálogo SICL. "
                f"Modelo alucinó. {explanation}"
            ),
            confidence=0.0,
            status="NO_MATCH",
        )

    return CopilotIntent(
        natural_language=text,
        command=command,
        explanation=explanation,
        confidence=confidence,
        status="PREVIEW_ONLY",
    )


class OllamaCopilot:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "deepseek-coder-v2:16b")
        self.timeout = timeout

    def translate_preview(self, text: str) -> CopilotIntent:
        if not text.strip():
            raise ValueError("natural language input is required")
        if not self.base_url:
            raise RuntimeError("COPILOT_NOT_CONFIGURED")

        system_prompt = _SYSTEM_PROMPT.format(catalog=catalog_for_prompt())

        body = {
            "model": self.model,
            "temperature": 0,
            "stream": False,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        }
        request = urllib.request.Request(
            self.base_url + "/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                response_payload = json.load(response)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RuntimeError(f"COPILOT_UNAVAILABLE: {exc}") from exc

        content = response_payload["choices"][0]["message"]["content"]
        return _validate(json.loads(content), text)


def intent_to_dict(intent: CopilotIntent) -> dict[str, Any]:
    return asdict(intent)
