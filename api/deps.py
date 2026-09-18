from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


_database_path = os.getenv("SICL_DB_PATH")
if not _database_path:
    database_url = os.getenv("DATABASE_URL", "")
    if database_url.startswith("sqlite:///"):
        _database_path = database_url.removeprefix("sqlite:///")
    elif database_url and "://" not in database_url:
        _database_path = database_url
    else:
        _database_path = "sicl.sqlite"

if _database_path != ":memory:":
    Path(_database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)

def get_repository() -> Generator[SQLiteRepository, None, None]:
    repository = SQLiteRepository(_database_path, check_same_thread=False)
    try:
        yield repository
    finally:
        repository.close()


def get_interpreter(repository: SQLiteRepository = None, actor: str = "api") -> CLI:
    return CLI(repository or SQLiteRepository(_database_path, check_same_thread=False), actor=actor)
