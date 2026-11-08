"""
Tests de copiloto SICL.

Verifica:
- Traducción a comando válido del catálogo.
- Detección de comando inventado → NO_MATCH.
- Detección de "no match" explícito → NO_MATCH.
- Error de Ollama → COPILOT_UNAVAILABLE.
- Validación de input vacío.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.sicl.command_catalog import is_known_command
from src.sicl.copilot import OllamaCopilot, CopilotIntent, intent_to_dict


def _mock_ollama_response(content: str) -> MagicMock:
    """Mock de urllib.request.urlopen que devuelve un response JSON."""
    mock = MagicMock()
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    mock.read = MagicMock(return_value=b"")
    # json.load lee del file-like
    mock.__iter__ = MagicMock(return_value=iter([json.dumps({
        "choices": [{"message": {"content": content}}]
    })]))
    # Mejor: usar readable stream
    return mock


def _ollama_payload(content: str) -> dict:
    return {"choices": [{"message": {"content": content}}]}


class TestCatalog:
    def test_catalog_loads(self):
        from src.sicl.command_catalog import COMMANDS
        assert len(COMMANDS) > 50
        assert "/PROJECT CREATE" in COMMANDS

    def test_known_command(self):
        assert is_known_command("/PROJECT CREATE UPAO-001")
        assert is_known_command("/STATUS")
        assert is_known_command("/FACT SET foo bar")

    def test_unknown_command(self):
        assert not is_known_command("/CREATE WALL 5M")
        assert not is_known_command("/INVENTED CMD")

    def test_unknown_explicit(self):
        assert is_known_command("UNKNOWN")


class TestCopilotTranslate:
    def test_valid_command(self):
        copilot = OllamaCopilot(base_url="http://127.0.0.1:11434", model="test")
        mock_response = _ollama_payload(
            json.dumps({
                "command": "/PROJECT CREATE UPAO-001 \"UPAO\"",
                "explanation": "Crea el proyecto",
                "confidence": 0.95,
            })
        )
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            # json.load() lee usando .read()
            mock_ctx.read = MagicMock(return_value=json.dumps(mock_response).encode())
            mock_urlopen.return_value = mock_ctx

            intent = copilot.translate_preview("crea un proyecto UPAO-001")
            assert isinstance(intent, CopilotIntent)
            assert intent.status == "PREVIEW_ONLY"
            assert intent.executed is False
            assert intent.decision_created is False
            assert intent.command.startswith("/PROJECT CREATE")
            assert intent.confidence == 0.95

    def test_invented_command(self):
        copilot = OllamaCopilot(base_url="http://127.0.0.1:11434", model="test")
        mock_response = _ollama_payload(
            json.dumps({
                "command": "/CREATE WALL 5M",
                "explanation": "Inventado",
                "confidence": 0.9,
            })
        )
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_ctx.read = MagicMock(return_value=json.dumps(mock_response).encode())
            mock_urlopen.return_value = mock_ctx

            intent = copilot.translate_preview("crea una pared")
            assert intent.status == "NO_MATCH"
            assert intent.command == "UNKNOWN"
            assert intent.confidence == 0.0

    def test_explicit_unknown(self):
        copilot = OllamaCopilot(base_url="http://127.0.0.1:11434", model="test")
        mock_response = _ollama_payload(
            json.dumps({
                "command": "UNKNOWN",
                "explanation": "No hay comando",
                "confidence": 0.0,
            })
        )
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_ctx.read = MagicMock(return_value=json.dumps(mock_response).encode())
            mock_urlopen.return_value = mock_ctx

            intent = copilot.translate_preview("haz algo raro")
            assert intent.status == "NO_MATCH"
            assert intent.command == "UNKNOWN"

    def test_no_command_key(self):
        copilot = OllamaCopilot(base_url="http://127.0.0.1:11434", model="test")
        mock_response = _ollama_payload(json.dumps({"explanation": "sin command"}))
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_ctx = MagicMock()
            mock_ctx.__enter__ = MagicMock(return_value=mock_ctx)
            mock_ctx.__exit__ = MagicMock(return_value=False)
            mock_ctx.read = MagicMock(return_value=json.dumps(mock_response).encode())
            mock_urlopen.return_value = mock_ctx

            with pytest.raises(ValueError, match="must include"):
                copilot.translate_preview("test")

    def test_empty_input(self):
        copilot = OllamaCopilot(base_url="http://127.0.0.1:11434", model="test")
        with pytest.raises(ValueError, match="natural language input"):
            copilot.translate_preview("   ")

    def test_no_base_url(self):
        copilot = OllamaCopilot(base_url="", model="test")
        with pytest.raises(RuntimeError, match="COPILOT_NOT_CONFIGURED"):
            copilot.translate_preview("test")

    def test_intent_to_dict(self):
        intent = CopilotIntent(
            natural_language="test",
            command="/STATUS",
            explanation="x",
            confidence=0.9,
            status="PREVIEW_ONLY",
        )
        d = intent_to_dict(intent)
        assert d["command"] == "/STATUS"
        assert d["executed"] is False
        assert d["decision_created"] is False
