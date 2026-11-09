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
from dataclasses import asdict, dataclass, field
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
    questions: list = field(default_factory=list)


_SYSTEM_PROMPT = """Eres ARKI, un Arquitecto Senior con 30 años de experiencia en diseño de hospitales, aeropuertos, puertos, terminales terrestres, vivienda y espacio público. Trabajas para Yvan Castillo en Trujillo, Perú.

Tu tarea es doble:
1. TRADUCIR la solicitud del usuario a UN comando SICL del catálogo (si es aplicable).
2. ACTUAR COMO ARQUITECTO: si la solicitud es un proyecto de diseño, analiza el brief y devuelve las PREGUNTAS CRÍTICAS que un arquitecto senior haría antes de diseñar (sitio, normativa, programa, usuarios, clima, presupuesto, sostenibilidad).

REGLAS:
- Devuelve SOLO JSON con las claves: command, explanation, confidence, questions.
- Si es un comando: command debe empezar con '/' y estar en el catálogo.
- Si es un proyecto de diseño (hospital, terminal, aeropuerto, etc.): command="UNKNOWN", confidence=0, y en 'questions' devuelve 3-5 preguntas técnicas concretas.
- NUNCA inventes comandos.
- NUNCA ejecutes. Solo propones.

CATÁLOGO SICL:
{catalog}

EJEMPLOS:
Solicitud: "Crea un proyecto UPAO-001"
Respuesta: {"command":"/PROJECT CREATE UPAO-001 UPAO","explanation":"Crear proyecto","confidence":0.95,"questions":[]}

Solicitud: "Quiero un hospital de 500 camas en Trujillo"
Respuesta: {"command":"UNKNOWN","explanation":"Proyecto de diseño. Necesito más información.","confidence":0,"questions":["¿Es público (MINSA/EsSalud) o privado?","¿Qué especialidades médicas requiere?","¿El terreno está en zona urbana consolidada o expansión?","¿Cuál es el presupuesto estimado en UIT?","¿Requiere helipuerto o área de emergencia aérea?"]}

Solicitud: "Registra el FAR=5"
Respuesta: {"command":"/FACT SET el FAR es 5 INSPECCION","explanation":"Registrar hecho","confidence":0.9,"questions":[]}
"""


def _validate(payload: Any, text: str) -> CopilotIntent:
    """Valida el payload del LLM. Tolera tanto dict como str (JSON serializado)."""
    # Si el LLM devolvió un string, intentar parsearlo como JSON
    if isinstance(payload, str):
        import json as _json
        try:
            payload = _json.loads(payload)
        except _json.JSONDecodeError:
            # Intentar extraer el primer objeto JSON que aparezca en el texto
            match_json = re.search(r'\{[^{}]*\}', payload, re.DOTALL)
            if match_json:
                try:
                    payload = _json.loads(match_json.group(0))
                except _json.JSONDecodeError:
                    raise ValueError(f"LLM output is not valid JSON: {payload[:200]}")

    if not isinstance(payload, dict):
        raise ValueError(f"LLM output must be a dict, got {type(payload).__name__}: {str(payload)[:200]}")

    command = str(payload.get("command", "")).strip()
    explanation = str(payload.get("explanation", "")).strip()
    try:
        confidence = float(payload.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    if not command:
        raise ValueError("copilot output must include 'command'")

    questions = payload.get("questions", [])
    if not isinstance(questions, list):
        questions = []

    # Caso UNKNOWN: el modelo admite que no hay match. NO es error.
    if command.upper() == "UNKNOWN":
        return CopilotIntent(
            natural_language=text,
            command="UNKNOWN",
            explanation=explanation,
            confidence=confidence,
            status="NO_MATCH",
            questions=questions,
        )

    if not is_known_command(command):
        raise ValueError(f"copilot output command is not in catalog: {command}")

    return CopilotIntent(
        natural_language=text,
        command=command,
        explanation=explanation,
        confidence=confidence,
        status="PREVIEW_ONLY",
        questions=questions,
    )




def _parse_llm_response(content: str, text: str) -> CopilotIntent:
    """Parseo tolerante de la respuesta del LLM.
    
    Acepta:
    - JSON puro: {"command": "/FACT SET ...", ...}
    - Texto con JSON embebido: "Aquí está: {...}"
    - Texto plano (no JSON): "Lo siento, no puedo..."
    """
    if content is None:
        content = ""
    content = str(content).strip()

    if not content:
        return CopilotIntent(
            natural_language=text,
            command="UNKNOWN",
            explanation="El modelo no devolvio contenido.",
            confidence=0.0,
            status="NO_MATCH",
            questions=[],
        )

    # 1. Intentar parseo directo como JSON
    try:
        payload = json.loads(content)
        return _validate(payload, text)
    except (json.JSONDecodeError, ValueError):
        pass

    # 2. Intentar extraer JSON embebido (bloques { ... })
    import re as _re
    json_candidates = _re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content, _re.DOTALL)
    for candidate in json_candidates:
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict) and ("command" in payload or "questions" in payload):
                return _validate(payload, text)
        except (json.JSONDecodeError, ValueError):
            continue

    # 3. Fallback: texto plano -> extraer preguntas (lineas que terminen en ?)
    questions = [
        line.strip()
        for line in content.split("\n")
        if line.strip().endswith("?")
    ]
    return CopilotIntent(
        natural_language=text,
        command="UNKNOWN",
        explanation=content[:500],
        confidence=0.0,
        status="NO_MATCH",
        questions=questions,
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

        system_prompt = _SYSTEM_PROMPT.replace("{catalog}", catalog_for_prompt())

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
        return _parse_llm_response(content, text)


def intent_to_dict(intent: CopilotIntent) -> dict[str, Any]:
    return asdict(intent)
