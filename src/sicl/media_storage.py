"""Minimal provider-neutral persistent media storage for local proof.

This adapter stores untrusted media outside public execution paths and exposes
only generated media identities. The canonical Evidence model stores the
retrieval reference and hash; bytes remain supporting infrastructure.
"""
from __future__ import annotations

import hashlib
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_MEDIA_BYTES = 10 * 1024 * 1024
_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{8,80}$")


@dataclass(frozen=True)
class StoredMedia:
    media_id: str
    storage_key: str
    content_type: str
    byte_size: int
    sha256: str
    original_filename: str


def media_root() -> Path:
    root = Path(os.environ.get("SICL_MEDIA_ROOT", Path(tempfile.gettempdir()) / "sicl-media"))
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def _validate_media_id(media_id: str) -> str:
    if not _SAFE_ID.fullmatch(media_id):
        raise ValueError("invalid media_id")
    return media_id


def _validate_content(content_type: str, size: int) -> None:
    if content_type not in ALLOWED_MIME:
        raise ValueError("unsupported media MIME")
    if size <= 0 or size > MAX_MEDIA_BYTES:
        raise ValueError("media exceeds configured size limit")


def store_media(media_id: str, content: bytes, content_type: str, original_filename: str = "upload") -> StoredMedia:
    media_id = _validate_media_id(media_id)
    _validate_content(content_type, len(content))
    # The generated identity is the only path component; the filename is metadata.
    suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[content_type]
    storage_key = f"{media_id}{suffix}"
    root = media_root()
    destination = (root / storage_key).resolve()
    if destination.parent != root:
        raise ValueError("unsafe media path")
    temp = destination.with_name(f".{destination.name}.{uuid4().hex}.tmp")
    temp.write_bytes(content)
    temp.replace(destination)
    return StoredMedia(media_id, storage_key, content_type, len(content), hashlib.sha256(content).hexdigest(), original_filename or "upload")


def retrieve_media(media_id: str) -> tuple[bytes, str, str]:
    media_id = _validate_media_id(media_id)
    root = media_root()
    matches = list(root.glob(f"{media_id}.*"))
    if len(matches) != 1 or matches[0].resolve().parent != root:
        raise FileNotFoundError(media_id)
    path = matches[0]
    content_type = {".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(path.suffix)
    if content_type is None:
        raise FileNotFoundError(media_id)
    return path.read_bytes(), content_type, path.name
