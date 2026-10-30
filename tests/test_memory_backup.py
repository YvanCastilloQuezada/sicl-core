from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from cryptography.fernet import Fernet, InvalidToken

from scripts.arki_memory_backup import create_backup, restore_and_verify


def _database(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.executescript("""
        PRAGMA user_version = 1;
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            project_id TEXT NOT NULL,
            type TEXT NOT NULL,
            payload TEXT NOT NULL,
            actor TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'USER_COMMAND'
        );
        CREATE TRIGGER events_no_update
        BEFORE UPDATE ON events
        BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
        CREATE TRIGGER events_no_delete
        BEFORE DELETE ON events
        BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
        INSERT INTO events(timestamp, project_id, type, payload, actor, source)
        VALUES ('2026-10-30T10:00:00Z', 'P1', 'DECISION_RECORDED', '{}', 'owner', 'TEST');
    """)
    connection.commit()
    connection.close()


def test_encrypted_backup_and_isolated_restore_are_verified(tmp_path, monkeypatch):
    monkeypatch.setenv("SICL_BACKUP_FERNET_KEY", Fernet.generate_key().decode("ascii"))
    source = tmp_path / "source.sqlite"
    _database(source)

    backup, manifest = create_backup(source, tmp_path / "backups")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert backup.exists()
    assert data["event_count"] == 1
    assert data["events_no_update"] == 1
    assert data["events_no_delete"] == 1

    restored = tmp_path / "isolated" / "restored.sqlite"
    facts = restore_and_verify(backup, manifest, restored)
    assert facts["integrity"] == "ok"
    assert facts["event_count"] == 1
    assert facts["last_event_id"] == 1


def test_restore_refuses_existing_target(tmp_path, monkeypatch):
    monkeypatch.setenv("SICL_BACKUP_FERNET_KEY", Fernet.generate_key().decode("ascii"))
    source = tmp_path / "source.sqlite"
    _database(source)
    backup, manifest = create_backup(source, tmp_path / "backups")
    target = tmp_path / "existing.sqlite"
    target.write_text("do not overwrite", encoding="utf-8")
    with pytest.raises(RuntimeError, match="RESTORE_TARGET_ALREADY_EXISTS"):
        restore_and_verify(backup, manifest, target)
    assert target.read_text(encoding="utf-8") == "do not overwrite"


def test_backup_ciphertext_tampering_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("SICL_BACKUP_FERNET_KEY", Fernet.generate_key().decode("ascii"))
    source = tmp_path / "source.sqlite"
    _database(source)
    backup, manifest = create_backup(source, tmp_path / "backups")
    backup.write_bytes(backup.read_bytes() + b"tamper")
    target = tmp_path / "restored.sqlite"
    with pytest.raises(RuntimeError, match="BACKUP_CIPHERTEXT_HASH_MISMATCH"):
        restore_and_verify(backup, manifest, target)
    assert not target.exists()
