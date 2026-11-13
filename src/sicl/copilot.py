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




_SYSTEM_PROMPT = """Eres ARKI, un asistente experto en arquitectura, ingeniería y normativa peruana (RNE, OECE, Invierte.pe).

Tu tarea es CLASIFICAR la intención del usuario y responder de forma estructurada.

INTENCIONES POSIBLES:
1. "DESIGN": El usuario quiere diseñar un proyecto (ej: "hospital de 5 pisos", "terminal de buses").
2. "SEARCH_NORMATIVE": El usuario quiere buscar normativa o regulaciones (ej: "busca normativa sobre estacionamientos", "qué dice el RNE sobre retiros").
3. "CHAT": El usuario saluda, pregunta qué puedes hacer, o hace una pregunta general (ej: "hola", "qué puedes hacer", "ayuda").

REGLAS:
- Devuelve SOLO JSON con las claves: action, explanation, confidence, parameters, query, questions.
- `action`: "DESIGN" | "SEARCH_NORMATIVE" | "CHAT".
- `explanation`: Una respuesta breve y amigable explicando qué vas a hacer.
- `confidence`: 0.95 si estás seguro, 0.5 si dudas.
- `parameters`: (solo si action es "DESIGN") objeto con los parámetros del proyecto. Si no es DESIGN, ponlo como {}.
- `query`: (solo si action es "SEARCH_NORMATIVE") el término de búsqueda de normativa. Si no es SEARCH_NORMATIVE, ponlo como null.
- `questions`: SIEMPRE [].

PARÁMETROS PARA "DESIGN":
- tipo: "terminal_terrestre" | "hospital" | "aeropuerto" | "puerto" | "vivienda" | "oficina" | "comercio" | "educacion" | "deporte" | "cultura" | "restaurante" | "hotel" | "otro"
- area_m2, pisos, capacidad, estilo, areas_verdes, feng_shui, parque_infantil, presupuesto_uit, ciudad, terreno_dimensiones. Si un dato falta, ponlo null.

EJEMPLOS:

Usuario: "Hola, qué puedes hacer?"
Respuesta:
{"action":"CHAT","explanation":"Hola. Soy ARKI. Puedo diseñar proyectos arquitectónicos (hospitales, terminales, viviendas), buscar normativa peruana (RNE, OECE), y analizar planos. ¿Qué necesitas?","confidence":0.95,"parameters":{},"query":null,"questions":[]}

Usuario: "Busca normativa sobre estacionamientos"
Respuesta:
{"action":"SEARCH_NORMATIVE","explanation":"Buscando normativa sobre estacionamientos en el RNE y OECE...","confidence":0.95,"parameters":{},"query":"estacionamientos","questions":[]}

Usuario: "Diseña un hospital de 5 pisos con 200 camas"
Respuesta:
{"action":"DESIGN","explanation":"Diseñando hospital de 5 pisos con 200 camas.","confidence":0.95,"parameters":{"tipo":"hospital","area_m2":null,"pisos":5,"capacidad":200,"estilo":null,"areas_verdes":null,"feng_shui":null,"parque_infantil":null,"presupuesto_uit":null,"ciudad":null,"terreno_dimensiones":null},"query":null,"questions":[]}
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
            explanation="El modelo no devolvio un JSON valido.",
            confidence=0.0,
            status="NO_MATCH",
            questions=[],
            parameters={},
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

        parameters = payload.get("parameters", {})
        if not isinstance(parameters, dict):
            parameters = {}

        if not command:
            return CopilotIntent(
                natural_language=text,
                command="UNKNOWN",
                explanation=explanation or "Sin comando.",
                confidence=confidence,
                status="NO_MATCH",
                questions=questions,
                parameters=parameters,
            )

        if command.upper() == "UNKNOWN":
            return CopilotIntent(
                natural_language=text,
                command="UNKNOWN",
                explanation=explanation or "Proyecto de diseno.",
                confidence=confidence,
                status="NO_MATCH",
                questions=questions,
                parameters=parameters,
            )

        if not is_known_command(command):
            return CopilotIntent(
                natural_language=text,
                command="UNKNOWN",
                explanation=f"Comando inventado: {command}. {explanation}",
                confidence=0.0,
                status="NO_MATCH",
                questions=questions,
                parameters=parameters,
            )

        return CopilotIntent(
            natural_language=text,
            command=command,
            explanation=explanation,
            confidence=confidence,
            status="PREVIEW_ONLY",
            questions=questions,
            parameters=parameters,
        )

    # CASO 2: JSON plano (solo parametros). El modelo extrajo los datos.
    # Envolverlo en el formato esperado por el frontend.
    return CopilotIntent(
        natural_language=text,
        command="UNKNOWN",
        explanation=f"Parametros extraidos: {str(payload)[:200]}",
        confidence=0.9,
        status="NO_MATCH",
        questions=[],
        parameters=payload,  # <-- AQUI SE GUARDAN LOS PARAMETROS
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
        timeout: float = 300.0,
    ) -> None:
        self.base_url = (base_url or "http://127.0.0.1:11435").rstrip("/")
        # Limpiar /v1 o /api si quedaron en la URL
        if self.base_url.endswith("/v1"):
            self.base_url = self.base_url[:-3]
        if self.base_url.endswith("/api"):
            self.base_url = self.base_url[:-4]
        self.model = model or "llama3:latest"
        self.timeout = timeout

    def translate_preview(self, text: str) -> CopilotIntent:
        if not text.strip():
            raise ValueError("natural language input is required")
        if not self.base_url:
            raise RuntimeError("COPILOT_NOT_CONFIGURED")

        import httpx
        system_prompt = _SYSTEM_PROMPT.replace("{catalog}", catalog_for_prompt())

        body = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        }
        
        url = self.base_url.rstrip("/") + "/api/chat"
        try:
            response = httpx.post(url, json=body, timeout=300.0)
            response.raise_for_status()
            response_payload = response.json()
        except httpx.HTTPStatusError as exc:
            # Extraer el detalle real de Ollama
            try:
                detail = exc.response.json().get("error", str(exc))
            except Exception:
                detail = str(exc)
            raise RuntimeError(f"COPILOT_UNAVAILABLE: {detail}") from exc
        except (httpx.RequestError, TimeoutError) as exc:
            raise RuntimeError(f"COPILOT_UNAVAILABLE: {exc}") from exc

        content = response_payload["message"]["content"]
        return _parse_llm_response(content, text)


def intent_to_dict(intent: CopilotIntent) -> dict[str, Any]:
    return asdict(intent)
