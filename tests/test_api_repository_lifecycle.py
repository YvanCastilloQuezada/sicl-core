from concurrent.futures import ThreadPoolExecutor
import sqlite3

from api import deps


def test_get_repository_creates_and_closes_request_scoped_connections(tmp_path, monkeypatch):
    database_path = tmp_path / "request-scoped.sqlite"
    monkeypatch.setattr(deps, "_database_path", str(database_path))

    def use_repository(_):
        dependency = deps.get_repository()
        repository = next(dependency)
        repository.conn.execute("SELECT 1").fetchone()
        connection = repository.conn
        try:
            next(dependency)
        except StopIteration:
            pass
        try:
            connection.execute("SELECT 1")
        except sqlite3.ProgrammingError:
            return True
        return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        closed = list(pool.map(use_repository, range(32)))

    assert all(closed)
    assert database_path.exists()
