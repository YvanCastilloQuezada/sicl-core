"""
Catálogo de comandos SICL, cargado desde commands-catalog.json.

Se usa en el copiloto para que el LLM no invente comandos que no existen
en el dominio real.

Uso:
    from sicl.command_catalog import COMMANDS, is_known_command
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path


# Ruta canónica del catálogo (relativa al repo)
_CATALOG_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "canonical" / "sicl-web" / "client" / "src" / "content" / "commands-catalog.json"
)

# Alternativa: buscar relativo al repo actual
_CATALOG_FALLBACK = Path(__file__).parent.parent.parent / "canonical" / "sicl-web" / "client" / "src" / "content" / "commands-catalog.json"


@lru_cache(maxsize=1)
def _load_catalog() -> list[dict]:
    """Carga commands-catalog.json. Retorna [] si no existe (modo offline)."""
    candidates = [_CATALOG_FALLBACK, _CATALOG_PATH]
    for p in candidates:
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
    return []


@lru_cache(maxsize=1)
def _build_command_map() -> dict[str, dict]:
    """Mapa de comando canónico (mayúsculas) → entrada del catálogo."""
    catalog = _load_catalog()
    result: dict[str, dict] = {}
    for entry in catalog:
        name = str(entry.get("name", "")).upper().strip()
        if name.startswith("/"):
            # Es el comando canónico
            result[name] = entry
        compact = str(entry.get("compact", "")).upper().strip()
        if compact and not compact.startswith("/"):
            # Alias compacto (ej. PRO-CRE) apunta al mismo comando
            result[compact] = entry
    return result


# Nombres canónicos (ej. "/PROJECT CREATE")
COMMANDS: tuple[str, ...] = tuple(
    sorted(k for k in _build_command_map().keys() if k.startswith("/"))
)

# Todos los aliases (canónicos + compactos)
ALL_ALIASES: tuple[str, ...] = tuple(sorted(_build_command_map().keys()))


def is_known_command(command: str) -> bool:
    """
    Verifica si un comando pertenece al catálogo SICL.

    Acepta:
    - "/PROJECT CREATE UPAO-001 ..."  → head "/PROJECT CREATE" en el catálogo
    - "PRO-CRE UPAO-001 ..."          → head "PRO-CRE" alias compacto
    - "UNKNOWN"                       → comando explícito de "no match"
    """
    if not command:
        return False
    normalized = command.strip()
    if normalized.upper() == "UNKNOWN":
        return True

    # Tomar los primeros 2 tokens para comandos multi-palabra (ej. /PROJECT CREATE)
    parts = normalized.split()
    if not parts:
        return False
    head_1 = parts[0].upper()
    head_2 = " ".join(parts[:2]).upper() if len(parts) >= 2 else head_1

    cmap = _build_command_map()
    return head_1 in cmap or head_2 in cmap


def catalog_for_prompt() -> str:
    """
    Retorna un bloque de texto con el catálogo para incluir en el
    system prompt del copiloto. Formato compacto.
    """
    catalog = _load_catalog()
    lines: list[str] = []
    for entry in catalog:
        name = entry.get("name", "")
        syntax = entry.get("syntax", "")
        if not name:
            continue
        # Formato: - /PROJECT CREATE: PRO-CRE <project_id> <name> [scopes]
        lines.append(f"- {name}: {syntax}")
    return "\n".join(lines)
