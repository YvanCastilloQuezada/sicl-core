"""
Catálogo de comandos SICL, cargado desde commands-catalog.json del frontend.

Se usa en el copiloto para que el LLM no invente comandos que no existen
en el dominio real.

Uso:
    from sicl.command_catalog import COMMANDS, is_known_command

Estrategia de búsqueda (en orden):
1. Variable de entorno SICL_COMMANDS_CATALOG (path absoluto).
2. Ruta relativa desde este archivo (asumiendo layout canonical/).
3. Ruta relativa desde el CWD (tests, scripts).
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path


def _candidate_paths() -> list[Path]:
    """Rutas candidatas para el catálogo de comandos SICL.
    
    Prioridad:
    1. Variable de entorno SICL_COMMANDS_CATALOG
    2. src/sicl/commands-catalog.json (catálogo plano, nativo del core)
    3. commands-catalog.json en la raíz del core
    4. sicl-web/client/src/content/commands-catalog.json (formato con categorías)
    """
    candidates: list[Path] = []

    # 1. Env var override (máxima prioridad)
    env_path = os.getenv("SICL_COMMANDS_CATALOG")
    if env_path:
        candidates.append(Path(env_path))

    # 2. Catálogo plano nativo del core (src/sicl/commands-catalog.json)
    here = Path(__file__).resolve()
    candidates.append(here.parent / "commands-catalog.json")  # sicl-core/src/sicl/commands-catalog.json

    # 3. Catálogo plano en la raíz del core
    candidates.append(here.parent.parent.parent / "commands-catalog.json")  # sicl-core/commands-catalog.json

    # 4. Fallback: catálogo del frontend (con categorías, requiere aplanado)
    for levels_up in (3, 4, 5):
        base = here
        for _ in range(levels_up):
            base = base.parent
        candidates.append(base / "sicl-web" / "client" / "src" / "content" / "commands-catalog.json")

    # 5. Relativo al CWD
    cwd = Path.cwd()
    candidates.append(cwd / "commands-catalog.json")
    candidates.append(cwd / "client" / "src" / "content" / "commands-catalog.json")
    candidates.append(cwd.parent / "sicl-web" / "client" / "src" / "content" / "commands-catalog.json")

    return candidates


@lru_cache(maxsize=1)
def _load_catalog() -> list[dict]:
    """Carga commands-catalog.json. Retorna [] si no se encuentra."""
    for p in _candidate_paths():
        try:
            resolved = p.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved.is_file():
            try:
                return json.loads(resolved.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
    return []


@lru_cache(maxsize=1)
def _build_command_map():
    """Construye el mapa de comandos, tolerante a ambos formatos:
    - Array plano: [{name, description}, ...]
    - Objeto con categorías: {categories: {cat: [{command/name, description}, ...]}}
    """
    raw = _load_catalog()
    commands = []

    # Formato 1: array plano
    if isinstance(raw, list):
        commands = raw

    # Formato 2: objeto con categorías
    elif isinstance(raw, dict):
        if "categories" in raw and isinstance(raw["categories"], dict):
            for cat_commands in raw["categories"].values():
                if isinstance(cat_commands, list):
                    commands.extend(cat_commands)
        elif "commands" in raw and isinstance(raw["commands"], list):
            commands = raw["commands"]

    # Construir el mapa
    result = {}
    for entry in commands:
        if not isinstance(entry, dict):
            continue
        # Aceptar tanto 'name' como 'command'
        name = str(entry.get("name") or entry.get("command") or "").upper().strip()
        if not name:
            continue
        # Normalizar para que empiece con /
        if not name.startswith("/"):
            name = "/" + name
        result[name] = entry

    return result


# Nombres canónicos (ej. "/PROJECT CREATE")
COMMANDS: tuple[str, ...] = tuple(
    sorted(k for k in _build_command_map().keys() if k.startswith("/"))
)

# Todos los aliases (canónicos + compactos)
ALL_ALIASES: tuple[str, ...] = tuple(sorted(_build_command_map().keys()))


def catalog_path() -> str | None:
    """Retorna el path del catálogo cargado, o None si no se encontró."""
    for p in _candidate_paths():
        try:
            resolved = p.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved.is_file():
            return str(resolved)
    return None


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

    parts = normalized.split()
    if not parts:
        return False
    head_1 = parts[0].upper()
    head_2 = " ".join(parts[:2]).upper() if len(parts) >= 2 else head_1

    cmap = _build_command_map()
    return head_1 in cmap or head_2 in cmap


def catalog_for_prompt() -> str:
    """Retorna un bloque de texto con el catálogo para el system prompt."""
    catalog = _load_catalog()
    lines: list[str] = []
    for entry in catalog:
        name = entry.get("name", "")
        syntax = entry.get("syntax", "")
        if not name:
            continue
        lines.append(f"- {name}: {syntax}")
    return "\n".join(lines)
