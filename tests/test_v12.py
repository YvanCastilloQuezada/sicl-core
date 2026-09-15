import json
from pathlib import Path

from sicl.cli import CLI
from sicl.repository import SQLiteRepository


def seed_v12(cli: CLI) -> None:
    cli.execute('/PROJECT CREATE V12 "UPAO v1.2"')
    cli.execute('/OBJECTIVE SET CLIMATE MAXIMIZE 80')
    cli.execute('/CONSTRAINT SET HEIGHT "<=" 6 FLOORS')
    cli.execute('/FACT SET "SITE_AREA=2000" CATASTRO')
    cli.execute('/ALTERNATIVE CREATE OPCION_A')
    cli.execute('/ALTERNATIVE CREATE OPCION_B')
    cli.execute('/EVALUATE OPCION_A CLIMATE 85')
    cli.execute('/EVALUATE OPCION_B CLIMATE 90')
    cli.execute('/COMPARE OPCION_A OPCION_B')
    cli.execute('/RECOMMEND')


def test_export_project_json(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "json.sqlite")
    cli = CLI(repo)
    seed_v12(cli)
    target = tmp_path / "exports" / "project.json"
    result = cli.execute(f'/EXPORT PROJECT "{target}"')
    assert result["code"] == "OK"
    payload = json.loads(target.read_text(encoding="utf-8"))
    for key in ("objectives", "constraints", "facts", "alternatives", "evaluations", "comparisons", "recommendations", "events"):
        assert key in payload
    repo.close()


def test_export_csv(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "csv.sqlite")
    cli = CLI(repo)
    seed_v12(cli)
    directory = tmp_path / "csv"
    result = cli.execute(f'/EXPORT CSV "{directory}"')
    assert result["code"] == "OK"
    for suffix in ("objectives", "constraints", "alternatives", "evaluations"):
        output = directory / f"V12_{suffix}.csv"
        assert output.exists()
        assert output.read_text(encoding="utf-8").strip()
    repo.close()


def test_export_report(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "report.sqlite")
    cli = CLI(repo)
    seed_v12(cli)
    target = tmp_path / "exports" / "report.txt"
    assert cli.execute(f'/EXPORT REPORT "{target}"')["code"] == "OK"
    content = target.read_text(encoding="utf-8")
    assert "V12" in content and "OBJECTIVES" in content and "RECOMMENDATIONS" in content
    repo.close()


def test_report_command(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "report-command.sqlite")
    cli = CLI(repo)
    seed_v12(cli)
    text = cli.execute('/REPORT')["data"]["text"]
    assert "SICL PROJECT REPORT" in text
    assert "Alternatives: 2" in text
    assert "Events:" in text
    repo.close()


def test_tradeoffs_command(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "tradeoffs.sqlite")
    cli = CLI(repo)
    seed_v12(cli)
    text = cli.execute('/TRADEOFFS')["data"]["text"]
    assert "SICL TRADE-OFFS" in text
    assert "OPCION_A" in text and "OPCION_B" in text
    repo.close()


def test_dashboard_command(tmp_path: Path):
    repo = SQLiteRepository(tmp_path / "dashboard.sqlite")
    cli = CLI(repo)
    seed_v12(cli)
    text = cli.execute('/DASHBOARD')["data"]["text"]
    assert "SICL DASHBOARD" in text
    assert "[" in text and "%" in text
    assert "Objectives=1" in text and "Alternatives=2" in text
    repo.close()
