"""Offline human-operated ACE88 key enrollment and explicit approval signing.

Never expose this CLI as an HTTP endpoint or agent tool.
"""
from __future__ import annotations

import argparse
import base64
import getpass
import json
import os
from pathlib import Path
import stat
import sys
import uuid
from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption, Encoding, NoEncryption, PrivateFormat, PublicFormat,
    load_pem_private_key,
)

from .human_authority_crypto import ACTION, CONTRACT, canonical_bytes
from .repository import SQLiteRepository


def _secret(prompt: str, *, confirm: bool = False) -> bytes:
    password = getpass.getpass(prompt)
    if len(password) < 16:
        raise ValueError('PASSPHRASE_TOO_SHORT: minimum 16 characters')
    if confirm and password != getpass.getpass('Repite la contraseña: '):
        raise ValueError('PASSPHRASE_MISMATCH')
    return password.encode('utf-8')


def _private_file(path: Path) -> None:
    if path.is_symlink():
        raise ValueError('SYMLINK_FORBIDDEN')
    if path.exists():
        raise ValueError('KEY_ALREADY_EXISTS')
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path.parent, 0o700)


def enroll(*, db: str, project: str, actor: str, key_id: str, key_file: str) -> None:
    path = Path(key_file).expanduser().resolve()
    _private_file(path)
    print(f'ENROLAR CLAVE: proyecto={project}, actor={actor}, keyId={key_id}')
    if input('Escribe REGISTRAR para confirmar: ').strip() != 'REGISTRAR':
        raise ValueError('HUMAN_CONFIRMATION_REQUIRED')
    password = _secret('Nueva contraseña de llave (>=16 caracteres): ', confirm=True)
    private = Ed25519PrivateKey.generate()
    encoded = private.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, BestAvailableEncryption(password))
    public = base64.b64encode(private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded)
        repo = SQLiteRepository(db)
        try:
            repo.register_authority_key_offline(project_id=project, key_id=key_id,
                                                 actor_id=actor, public_key_b64=public)
        finally:
            repo.close()
    except Exception:
        path.unlink(missing_ok=True)
        raise
    print('OWNER_KEY_ENROLLED; la clave privada cifrada permanece solo en esta máquina.')


def sign(*, request_file: str, key_file: str, output_file: str) -> None:
    key_path = Path(key_file).expanduser()
    mode = key_path.stat().st_mode
    if key_path.is_symlink() or (stat.S_IMODE(mode) & 0o077):
        raise ValueError('INSECURE_KEY_FILE_PERMISSIONS')
    request = json.loads(Path(request_file).read_text(encoding='utf-8'))
    expected = {'projectId', 'proposalId', 'fingerprint', 'actorId', 'reviewId', 'keyId'}
    if set(request) != expected or not all(isinstance(v, str) and v.strip() for v in request.values()):
        raise ValueError('INVALID_SIGNING_REQUEST')
    if len(request['fingerprint']) != 64 or any(c not in '0123456789abcdef' for c in request['fingerprint']):
        raise ValueError('INVALID_FINGERPRINT')
    now = datetime.now(timezone.utc)
    payload = {
        'contract': CONTRACT, 'action': ACTION, **request,
        'decision': 'APPROVED', 'issuedAt': now.isoformat(),
        'expiresAt': (now + timedelta(minutes=3)).isoformat(),
        'nonce': uuid.uuid4().hex,
    }
    print('APROBACIÓN HUMANA D2 — REVISAR DETENIDAMENTE:')
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if input('Escribe APROBAR D2 para firmar esta propuesta: ').strip() != 'APROBAR D2':
        raise ValueError('HUMAN_CONFIRMATION_REQUIRED')
    password = _secret('Contraseña de llave: ')
    private = load_pem_private_key(key_path.read_bytes(), password=password)
    if not isinstance(private, Ed25519PrivateKey):
        raise ValueError('WRONG_KEY_TYPE')
    signature = base64.b64encode(private.sign(canonical_bytes(payload))).decode()
    output = Path(output_file).expanduser()
    if output.is_symlink() or output.exists():
        raise ValueError('OUTPUT_EXISTS_OR_SYMLINK')
    fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump({'approval_payload': payload, 'approval_signature_b64': signature}, stream, indent=2)
    print(f'SIGNED_APPROVAL_WRITTEN={output}')


def main() -> int:
    parser = argparse.ArgumentParser(description='ACE88 offline owner approval (never run by an agent)')
    sub = parser.add_subparsers(dest='command', required=True)
    e = sub.add_parser('enroll')
    for opt in ('db', 'project', 'actor', 'key-id', 'key-file'):
        e.add_argument('--' + opt, required=True)
    s = sub.add_parser('sign')
    for opt in ('request-file', 'key-file', 'output-file'):
        s.add_argument('--' + opt, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'enroll':
            enroll(db=args.db, project=args.project, actor=args.actor,
                   key_id=args.key_id, key_file=args.key_file)
        else:
            sign(request_file=args.request_file, key_file=args.key_file,
                 output_file=args.output_file)
    except Exception as exc:
        print(f'ACE88_BLOCKED: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
