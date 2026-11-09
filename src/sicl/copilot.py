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
    parameters: dict = field(default_factory=dict)




_SYSTEM_PROMPT = """Eres un EXTRACTOR DE PARÁMETROS ARQUITECTÓNICOS.

Devuelve SOLO el JSON con los parámetros extraídos. Sin explicaciones, sin markdown, sin bloques de código. El JSON debe tener SOLO estas claves:

- tipo: "terminal_terrestre" | "hospital" | "aeropuerto" | "puerto" | "vivienda" | "otro"
- area_m2: número o null
- buses_interprovinciales: número o null
- buses_provinciales: número o null
- taxis: número o null
- estilo: string o null
- areas_verdes: true | false | null
- feng_shui: true | false | null
- parque_infantil: true | false | null
- presupuesto_uit: número o null
- ciudad: string o null

EJEMPLO:
Solicitud: "Quiero un terminal terrestre para 120 buses interprovinciales, 60 provinciales y 240 taxis, en 120,000 m², estilo neo futurista con áreas verdes y feng shui, y parque infantil interno"
Respuesta:
{"tipo":"terminal_terrestre","area_m2":120000,"buses_interprovinciales":120,"buses_provinciales":60,"taxis":240,"estilo":"neo_futurista","areas_verdes":true,"feng_shui":true,"parque_infantil":true,"presupuesto_uit":null,"ciudad":null}
"""




def _validate(payload: Any, text: str) -> CopilotIntent:
    """Valida el payload del LLM. Tolera:
    - JSON con formato completo: {command, explanation, confidence, parameters, questions}
    - JSON plano (solo parámetros): {tipo, area_m2, ...}
    - Texto plano
    """
    if isinstance(payload, str):
        import json as _json
        try:
            payload = _json.loads(payload)
        except _json.JSONDecodeError:
            match_json = re.search(r'\{[^{}]*\}', payload, re.DOTALL)
            if match_json:
                try:
                    payload = _json.loads(match_json.group(0))
                except _json.JSONDecodeError:
                    pass

    if not isinstance(payload, dict):
        return CopilotIntent(
            natural_language=text,
            command="UNKNOWN",
            explanation="El modelo no devolvió un JSON válido.",
            confidence=0.0,
            status="NO_MATCH",
            questions=[],
        )

    # CASO 1: JSON con formato completo (tiene 'command' o 'questions')
    if "command" in payload or "questions" in payload:
        command = str(payload.get("command", "")).strip()
        explanation = str(payload.get("explanation", "")).strip()
        try:
            confidence = float(payload.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        questions = payload.get("questions", [])
        if not isinstance(questions, list):
            questions = []

        if not command:
            return CopilotIntent(
                natural_language=text,
                command="UNKNOWN",
                explanation=explanation or "Sin comando.",
                confidence=confidence,
                status="NO_MATCH",
                questions=questions,
            )

        if command.upper() == "UNKNOWN":
            return CopilotIntent(
                natural_language=text,
                command="UNKNOWN",
                explanation=explanation or "Proyecto de diseño.",
                confidence=confidence,
                status="NO_MATCH",
                questions=questions,
            )

        if not is_known_command(command):
            return CopilotIntent(
                natural_language=text,
                command="UNKNOWN",
                explanation=f"Comando inventado: {command}. {explanation}",
                confidence=0.0,
                status="NO_MATCH",
                questions=questions,
            )

        return CopilotIntent(
            natural_language=text,
            command=command,
            explanation=explanation,
            confidence=confidence,
            status="PREVIEW_ONLY",
            questions=questions,
        )

    # CASO 2: JSON plano (solo parámetros). El modelo extrajo los datos.
    # Envolverlo en el formato esperado por el frontend.
    return CopilotIntent(
        natural_language=text,
        command="UNKNOWN",
        explanation=f"Parámetros extraídos: {json.dumps(payload, ensure_ascii=False)[:200]}",
        confidence=0.9,
        status="NO_MATCH",
        questions=[],
        parameters=payload,  # <-- NUEVO: guardar el JSON plano como parámetros
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
