from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


def database_path() -> Path:
    configured = os.getenv("SICL_DB_PATH", "").strip()
    if not configured:
        database_url = os.getenv("DATABASE_URL", "").strip()
        if database_url.startswith("sqlite:///"):
            configured = database_url.removeprefix("sqlite:///")
        elif database_url and "://" not in database_url:
            configured = database_url
        else:
            configured = "sicl.sqlite"
    if configured == ":memory:":
        raise RuntimeError("BACKUP_IN_MEMORY_DATABASE_UNSUPPORTED")
    return Path(configured).expanduser().resolve()


def encryption() -> Fernet:
    key = os.getenv("SICL_BACKUP_FERNET_KEY", "").strip()
    if not key:
        raise RuntimeError("SICL_BACKUP_FERNET_KEY_REQUIRED")
    try:
        return Fernet(key.encode("ascii"))
    except Exception as exc:
        raise RuntimeError("SICL_BACKUP_FERNET_KEY_INVALID") from exc


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inspect_database(path: Path) -> dict[str, int | str]:
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"BACKUP_INTEGRITY_CHECK_FAILED:{integrity}")
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "events" not in tables:
            raise RuntimeError("BACKUP_EVENT_STORE_MISSING")
        event_count = int(connection.execute("SELECT COUNT(*) FROM events").fetchone()[0])
        last_event_id = int(connection.execute("SELECT COALESCE(MAX(id),0) FROM events").fetchone()[0])
        triggers = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
        return {
            "integrity": integrity,
            "user_version": int(connection.execute("PRAGMA user_version").fetchone()[0]),
            "event_count": event_count,
            "last_event_id": last_event_id,
            "events_no_update": int("events_no_update" in triggers),
            "events_no_delete": int("events_no_delete" in triggers),
        }
    finally:
        connection.close()


def create_backup(source: Path, output_dir: Path) -> tuple[Path, Path]:
    if not source.is_file():
        raise RuntimeError("SICL_DATABASE_FILE_NOT_FOUND")
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    plain_path = output_dir / f"sicl-core-{stamp}.sqlite.tmp"
    encrypted_path = output_dir / f"sicl-core-{stamp}.sqlite.fernet"
    manifest_path = output_dir / f"sicl-core-{stamp}.manifest.json"
    if encrypted_path.exists() or manifest_path.exists():
        raise RuntimeError("BACKUP_NAME_COLLISION")

    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    dst = sqlite3.connect(plain_path)
    try:
        src.backup(dst)
        dst.commit()
    finally:
        dst.close()
        src.close()

    plain = plain_path.read_bytes()
    facts = inspect_database(plain_path)
    encrypted = encryption().encrypt(plain)
    encrypted_path.write_bytes(encrypted)
    manifest = {
        "format": "SICL_CORE_FERNET_SQLITE_BACKUP_V1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_name": source.name,
        "encrypted_file": encrypted_path.name,
        "encrypted_sha256": sha256(encrypted),
        "plaintext_sha256": sha256(plain),
        "plaintext_bytes": len(plain),
        **facts,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plain_path.unlink()
    return encrypted_path, manifest_path


def restore_and_verify(backup: Path, manifest_path: Path, target: Path) -> dict[str, int | str]:
    if target.exists():
        raise RuntimeError("RESTORE_TARGET_ALREADY_EXISTS")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    encrypted = backup.read_bytes()
    if sha256(encrypted) != manifest.get("encrypted_sha256"):
        raise RuntimeError("BACKUP_CIPHERTEXT_HASH_MISMATCH")
    try:
        plain = encryption().decrypt(encrypted)
    except InvalidToken as exc:
        raise RuntimeError("BACKUP_DECRYPTION_FAILED") from exc
    if sha256(plain) != manifest.get("plaintext_sha256"):
        raise RuntimeError("BACKUP_PLAINTEXT_HASH_MISMATCH")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(plain)
    facts = inspect_database(target)
    for key in ("user_version", "event_count", "last_event_id", "events_no_update", "events_no_delete"):
        if facts[key] != manifest[key]:
            target.unlink(missing_ok=True)
            raise RuntimeError(f"RESTORE_MANIFEST_MISMATCH:{key}")
    return facts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Encrypted, verifiable SICL Core SQLite backup/restore")
    sub = parser.add_subparsers(dest="command", required=True)
    backup_parser = sub.add_parser("backup")
    backup_parser.add_argument("--output-dir", default=os.getenv("SICL_BACKUP_DIR", "backups/sicl-core"))
    restore_parser = sub.add_parser("restore-verify")
    restore_parser.add_argument("--backup", required=True)
    restore_parser.add_argument("--manifest", required=True)
    restore_parser.add_argument("--target", required=True)
    args = parser.parse_args(argv)

    if args.command == "backup":
        encrypted, manifest = create_backup(database_path(), Path(args.output_dir).expanduser().resolve())
        print(json.dumps({"status": "BACKUP_VERIFIED", "backup": encrypted.name, "manifest": manifest.name}))
        return 0

    facts = restore_and_verify(
        Path(args.backup).expanduser().resolve(),
        Path(args.manifest).expanduser().resolve(),
        Path(args.target).expanduser().resolve(),
    )
    print(json.dumps({"status": "RESTORE_VERIFIED", **facts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
