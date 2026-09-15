from __future__ import annotations

from collections.abc import Generator

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


_repository = SQLiteRepository(check_same_thread=False)


def get_repository() -> Generator[SQLiteRepository, None, None]:
    yield _repository


def get_interpreter(repository: SQLiteRepository = None, actor: str = "api") -> CLI:
    return CLI(repository or _repository, actor=actor)
