from __future__ import annotations

import sqlite3

from fastapi.testclient import TestClient

from api.deps import get_repository
from api.main import app
from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def test_regulation_minimal_is_unverified(tmp_path):
    repo = SQLiteRepository(tmp_path / "reg.sqlite")
    cli = CLI(repo)
    try:
        cli.execute('/PROJECT CREATE P-REG "Regulatory"')
        result = cli.execute('/REGULATION ADD RNE-001 RNE "Reglamento de prueba" Peru')
        assert result["code"] == "OK"
        assert result["data"]["regulation"]["status"] == "NO_VERIFICADA"
        assert result["data"]["regulation"]["source_type"] == "UNKNOWN"
    finally:
        repo.close()


def test_regulation_status_is_versioned_and_not_updated(tmp_path):
    repo = SQLiteRepository(tmp_path / "status.sqlite")
    cli = CLI(repo)
    try:
        cli.execute('/PROJECT CREATE P-REG "Regulatory"')
        cli.execute('/REGULATION ADD R-1 G.010 "Norma" Peru')
        result = cli.execute('/REGULATION STATUS R-1 MODIFICADA')
        assert result["code"] == "OK"
        assert result["data"]["regulation"]["version_field"] == 2
        assert repo.conn.execute("SELECT COUNT(*) FROM regulations WHERE regulation_id='R-1'").fetchone()[0] == 2
    finally:
        repo.close()


def test_interpretation_has_mandatory_disclaimer_and_requires_review(tmp_path):
    repo = SQLiteRepository(tmp_path / "interpret.sqlite")
    cli = CLI(repo)
    try:
        cli.execute('/PROJECT CREATE P-REG "Regulatory"')
        cli.execute('/REGULATION ADD R-1 G.010 "Norma" Peru')
        created = cli.execute('/INTERPRET ADD I-1 R-1 ART-1 "Texto interpretativo"')
        assert created["data"]["interpretation"]["state"] == "DRAFT"
        assert created["data"]["interpretation"]["disclaimer"] == "No constituye certificación legal ni reemplaza revisión profesional."
        reviewed = cli.execute('/INTERPRET REVIEW I-1 Architect ProfessionalAuthority')
        assert reviewed["data"]["interpretation"]["state"] == "REVIEWED"
        assert reviewed["data"]["applicable"] is True
    finally:
        repo.close()


def test_interpretation_never_creates_constraint(tmp_path):
    repo = SQLiteRepository(tmp_path / "no-constraint.sqlite")
    cli = CLI(repo)
    try:
        cli.execute('/PROJECT CREATE P-REG "Regulatory"')
        cli.execute('/REGULATION ADD R-1 G.010 "Norma" Peru')
        cli.execute('/INTERPRET ADD I-1 R-1 ART-1 "Debe respetarse"')
        cli.execute('/INTERPRET REVIEW I-1 Architect Authority')
        project = repo.get_project("P-REG")
        assert project is not None
        assert project.constraints == {}
    finally:
        repo.close()


def test_snapshot_freeze_is_immutable_and_preserves_prior_version(tmp_path):
    repo = SQLiteRepository(tmp_path / "snapshot.sqlite")
    cli = CLI(repo)
    try:
        cli.execute('/PROJECT CREATE P-REG "Regulatory"')
        cli.execute('/REGULATION ADD R-1 G.010 "Norma" Peru')
        created = cli.execute('/SNAPSHOT CREATE SNAP-1 P-REG 2026-09-15')
        assert created["code"] == "OK"
        frozen = cli.execute('/SNAPSHOT FREEZE SNAP-1 Reviewer')
        assert frozen["data"]["snapshot"]["state"] == "FROZEN"
        rejected = cli.execute('/SNAPSHOT FREEZE SNAP-1 Reviewer2')
        assert rejected["code"] == "INVALID_STATE"
        assert repo.conn.execute("SELECT COUNT(*) FROM normative_snapshots WHERE snapshot_id='SNAP-1'").fetchone()[0] == 2
        assert repo.conn.execute("SELECT state FROM normative_snapshots WHERE snapshot_id='SNAP-1' AND version=1").fetchone()[0] == "DRAFT"
    finally:
        repo.close()


def test_snapshot_does_not_change_when_regulation_status_changes(tmp_path):
    repo = SQLiteRepository(tmp_path / "snapshot-history.sqlite")
    cli = CLI(repo)
    try:
        cli.execute('/PROJECT CREATE P-REG "Regulatory"')
        cli.execute('/REGULATION ADD R-1 G.010 "Norma" Peru')
        cli.execute('/SNAPSHOT CREATE SNAP-1 P-REG 2026-09-15')
        cli.execute('/SNAPSHOT FREEZE SNAP-1 Reviewer')
        cli.execute('/REGULATION STATUS R-1 DEROGADA')
        snapshot = repo.get_normative_snapshot("SNAP-1")
        assert snapshot is not None
        assert snapshot.regulations_included == ["R-1"]
        assert snapshot.state.value == "FROZEN"
    finally:
        repo.close()


def test_append_only_triggers_for_regulatory_tables(tmp_path):
    repo = SQLiteRepository(tmp_path / "append.sqlite")
    cli = CLI(repo)
    try:
        cli.execute('/PROJECT CREATE P-REG "Regulatory"')
        cli.execute('/REGULATION ADD R-1 G.010 "Norma" Peru')
        cli.execute('/INTERPRET ADD I-1 R-1 ART-1 "Texto"')
        cli.execute('/SNAPSHOT CREATE SNAP-1 P-REG 2026-09-15')
        for sql, params in [
            ("UPDATE regulations SET title='x'", ()),
            ("DELETE FROM normative_interpretations", ()),
            ("UPDATE normative_snapshots SET state='FROZEN'", ()),
        ]:
            try:
                repo.conn.execute(sql, params)
                repo.conn.commit()
                assert False, sql
            except sqlite3.IntegrityError:
                repo.conn.rollback()
    finally:
        repo.close()


def test_regulatory_http_endpoints_and_envelope(tmp_path, monkeypatch):
    monkeypatch.delenv("SICL_CORE_SERVICE_TOKEN", raising=False)
    repo = SQLiteRepository(tmp_path / "api.sqlite", check_same_thread=False)
    app.dependency_overrides[get_repository] = lambda: repo
    client = TestClient(app)
    try:
        project = client.post('/v1/projects', json={"project_id": "P-API", "name": "API project"})
        assert project.status_code in (200, 201)
        created = client.post('/v1/regulations', json={"project_id": "P-API", "regulation_id": "R-API", "code": "RNE", "title": "Norma API"})
        assert created.status_code == 200
        assert created.json()["data"]["regulation"]["status"] == "NO_VERIFICADA"
        assert client.get('/v1/regulations').status_code == 200
        assert client.get('/v1/regulations/R-API').status_code == 200
        assert client.post('/v1/regulations/R-API/interpretations', json={"interpretation_id": "I-API", "article_reference": "A-1", "interpretation_text": "Texto"}).status_code == 200
        assert client.get('/v1/regulations/R-API/interpretations').status_code == 200
        reviewed = client.post('/v1/interpretations/I-API/review', json={"actor": "Architect", "authority": "Professional"})
        assert reviewed.status_code == 200
        snap = client.post('/v1/projects/P-API/normative-snapshots', json={"snapshot_id": "S-API", "cut_date": "2026-09-15"})
        assert snap.status_code == 200
        assert client.get('/v1/projects/P-API/normative-snapshots').status_code == 200
        frozen = client.post('/v1/normative-snapshots/S-API/freeze', json={"reviewer": "Reviewer"})
        assert frozen.status_code == 200
        assert frozen.json()["data"]["snapshot"]["state"] == "FROZEN"
    finally:
        app.dependency_overrides.clear()
        repo.close()
