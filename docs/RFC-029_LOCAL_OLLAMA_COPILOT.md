# RFC-029 — Copiloto LLM local para traducción a SICL

**Estado:** IMPLEMENTED — preview only

## Objetivo

RFC-029 añade un copiloto local basado en Ollama para traducir lenguaje natural a un comando SICL candidato. El modelo no ejecuta comandos, no crea decisiones, no modifica el repositorio y no sustituye la validación determinista del Core.

## Arquitectura

```text
Usuario → Ollama local → JSON de intención → revisión de comando → SICL Core determinista
                                               │
                                               └── nunca ejecuta automáticamente
```

Ollama documenta una interfaz compatible con OpenAI para chat completions y respuestas JSON [1]. El adaptador utiliza `POST /v1/chat/completions`, temperatura cero y un prompt que exige un único comando SICL.

## Contrato

```http
POST /v1/copilot/translate
```

Entrada:

```json
{"text":"crea un proyecto de vivienda en Trujillo", "model":"llama3.2:3b"}
```

Salida:

```json
{
  "intent": {
    "natural_language": "...",
    "command": "/PROJECT CREATE ...",
    "explanation": "...",
    "confidence": 0.86,
    "status": "PREVIEW_ONLY",
    "executed": false,
    "decision_created": false
  }
}
```

## Seguridad

El endpoint nunca llama a `CLI.execute`. La respuesta se presenta como preview. El usuario debe revisar el comando y ejecutarlo mediante el flujo SICL autorizado. El Core continúa rechazando comandos inválidos y conserva la autoridad humana para `HumanReview` y `Decision`.

Si `OLLAMA_BASE_URL` no está configurado, el endpoint devuelve `COPILOT_NOT_CONFIGURED`. Si Ollama no responde, devuelve `COPILOT_UNAVAILABLE`. Ningún token del servidor se envía al navegador.

## Configuración

```text
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

El modelo es una preferencia operativa. La determinación de validez, factibilidad, normas y decisiones permanece en SICL.

## Limitaciones deliberadas

El copiloto no afirma cumplimiento normativo, no interpreta automáticamente el RNE, no cambia objetivos o restricciones sin revisión y no aplica cambios BIM. Su resultado es una propuesta lingüística trazable.

## References

[1]: https://docs.ollama.com/api/openai-compatibility "Ollama OpenAI compatibility documentation"
