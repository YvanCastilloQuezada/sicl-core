from __future__ import annotations

import os
from collections.abc import Generator

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

_repository = SQLiteRepository(_database_path, check_same_thread=False)


def get_repository() -> Generator[SQLiteRepository, None, None]:
    yield _repository


def get_interpreter(repository: SQLiteRepository = None, actor: str = "api") -> CLI:
    return CLI(repository or _repository, actor=actor)
