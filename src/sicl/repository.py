from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterator

from .domain import Assumption, Constraint, Decision, Evidence, EvidenceType, Event, Fact, HumanReview, Objective, Preference, Project, Role, Source, SourceType, SpatialScope, TemporalScope
from .errors import SICLError
from .v11 import Alternative, Comparison, Evaluation, Recommendation
from .simulation import Simulation, SimulationState, SimulationType


class SQLiteRepository:
    def __init__(self, path: str | Path = ":memory:", check_same_thread: bool = True) -> None:
        self.path = str(path)
        self.conn = sqlite3.connect(self.path, check_same_thread=check_same_thread)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def close(self) -> None:
        self.conn.close()

    def _create_schema(self) -> None:
        self.conn.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS projects (
          project_id TEXT PRIMARY KEY, name TEXT NOT NULL,
          stage TEXT NOT NULL, version INTEGER NOT NULL,
          spatial_scope TEXT NULL,
          temporal_scope TEXT NOT NULL DEFAULT 'proyecto'
        );
        CREATE TABLE IF NOT EXISTS objectives (
          objective_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          key TEXT NOT NULL, direction TEXT NOT NULL, value TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS constraints_ (
          constraint_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          key TEXT NOT NULL, operator TEXT NOT NULL, value TEXT NOT NULL,
          unit TEXT NOT NULL, hard INTEGER NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS roles (
          role_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          name TEXT NOT NULL, actor TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS facts (
          fact_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          statement TEXT NOT NULL, source TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS assumptions (
          assumption_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          statement TEXT NOT NULL, basis TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS preferences (
          preference_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          statement TEXT NOT NULL, actor TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS decisions (
          decision_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          statement TEXT NOT NULL, actor TEXT NOT NULL, authority TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS human_reviews (
          review_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          actor TEXT NOT NULL, timestamp TEXT NOT NULL, review TEXT NOT NULL, reason TEXT NOT NULL,
          authority TEXT NOT NULL,
          status TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alternatives (
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          name TEXT NOT NULL, description TEXT NOT NULL, parameters_json TEXT NOT NULL,
          status TEXT NOT NULL, version INTEGER NOT NULL,
          source TEXT NOT NULL DEFAULT 'USER_COMMAND'
        );
        CREATE TABLE IF NOT EXISTS evaluations (
          id TEXT PRIMARY KEY, alternative_id TEXT NOT NULL REFERENCES alternatives(id),
          objective_id TEXT NOT NULL, value REAL NOT NULL, unit TEXT NOT NULL,
          confidence REAL NOT NULL, source TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS comparisons (
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          alternative_ids_json TEXT NOT NULL, evaluations_json TEXT NOT NULL,
          tradeoffs_json TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS recommendations (
          id TEXT PRIMARY KEY, comparison_id TEXT NOT NULL REFERENCES comparisons(id),
          recommended_alternative_id TEXT NOT NULL, reason TEXT NOT NULL,
          confidence REAL NOT NULL, status TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sources (
          source_id TEXT NOT NULL, project_id TEXT NOT NULL REFERENCES projects(project_id),
          source_type TEXT NOT NULL, title TEXT NOT NULL, url TEXT NULL, version INTEGER NOT NULL,
          PRIMARY KEY (project_id, source_id)
        );
        CREATE TABLE IF NOT EXISTS evidence (
          evidence_id TEXT NOT NULL, project_id TEXT NOT NULL REFERENCES projects(project_id),
          source_id TEXT NULL, statement TEXT NOT NULL, evidence_type TEXT NOT NULL,
          captured_at TEXT NOT NULL, method_version TEXT NOT NULL, evidence_url TEXT NULL,
          evidence_hash TEXT NULL, state TEXT NOT NULL, version INTEGER NOT NULL,
          PRIMARY KEY (project_id, evidence_id)
        );
        CREATE TABLE IF NOT EXISTS simulations (
          simulation_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          simulation_type TEXT NOT NULL, method TEXT NOT NULL, method_version TEXT NOT NULL,
          inputs_json TEXT NOT NULL, outputs_json TEXT NOT NULL, state TEXT NOT NULL,
          started_at TEXT NOT NULL, finished_at TEXT NULL, evidence_hash TEXT NOT NULL,
          version INTEGER NOT NULL
        );
        CREATE TRIGGER IF NOT EXISTS simulations_no_update
        BEFORE UPDATE ON simulations
        BEGIN SELECT RAISE(ABORT, 'simulations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS simulations_no_delete
        BEFORE DELETE ON simulations
        BEGIN SELECT RAISE(ABORT, 'simulations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS evidence_no_update
        BEFORE UPDATE ON evidence
        BEGIN SELECT RAISE(ABORT, 'evidence is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS evidence_no_delete
        BEFORE DELETE ON evidence
        BEGIN SELECT RAISE(ABORT, 'evidence is append-only'); END;
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL,
          project_id TEXT NOT NULL, type TEXT NOT NULL, payload TEXT NOT NULL,
          actor TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'USER_COMMAND'
        );
        CREATE TRIGGER IF NOT EXISTS events_no_update
        BEFORE UPDATE ON events
        BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS events_no_delete
        BEFORE DELETE ON events
        BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
        """)
        columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(events)")}
        if "source" not in columns:
            self.conn.execute("ALTER TABLE events ADD COLUMN source TEXT NOT NULL DEFAULT 'USER_COMMAND'")
        alternative_columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(alternatives)")}
        if "source" not in alternative_columns:
            self.conn.execute("ALTER TABLE alternatives ADD COLUMN source TEXT NOT NULL DEFAULT 'USER_COMMAND'")
        project_columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(projects)")}
        if "spatial_scope" not in project_columns:
            self.conn.execute("ALTER TABLE projects ADD COLUMN spatial_scope TEXT NULL")
        if "temporal_scope" not in project_columns:
            self.conn.execute("ALTER TABLE projects ADD COLUMN temporal_scope TEXT NOT NULL DEFAULT 'proyecto'")
        self.conn.commit()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            self.conn.execute("BEGIN")
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def add_event(self, event: Event) -> Event:
        cur = self.conn.execute(
            "INSERT INTO events(timestamp, project_id, type, payload, actor, source) VALUES (?, ?, ?, ?, ?, ?)",
            (event.timestamp, event.project_id, event.type, json.dumps(event.payload, sort_keys=True), event.actor, event.source),
        )
        return Event(cur.lastrowid, event.timestamp, event.project_id, event.type, event.payload, event.actor, event.source)

    def events(self, project_id: str | None = None) -> list[Event]:
        if project_id:
            rows = self.conn.execute("SELECT * FROM events WHERE project_id=? ORDER BY id", (project_id,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM events ORDER BY id").fetchall()
        return [Event(r["id"], r["timestamp"], r["project_id"], r["type"], json.loads(r["payload"]), r["actor"], r["source"]) for r in rows]

    def get_project(self, project_id: str) -> Project | None:
        row = self.conn.execute("SELECT * FROM projects WHERE project_id=?", (project_id,)).fetchone()
        if not row:
            return None
        spatial_scope = SpatialScope(row["spatial_scope"]) if row["spatial_scope"] else None
        temporal_scope = TemporalScope(row["temporal_scope"] or TemporalScope.PROYECTO.value)
        p = Project(row["project_id"], row["name"], row["stage"], row["version"], spatial_scope=spatial_scope, temporal_scope=temporal_scope)
        p.objectives = {r["objective_id"]: Objective(**dict(r)) for r in self.conn.execute("SELECT * FROM objectives WHERE project_id=?", (project_id,))}
        p.constraints = {r["constraint_id"]: Constraint(r["constraint_id"], r["project_id"], r["key"], r["operator"], r["value"], r["unit"], bool(r["hard"]), r["version"]) for r in self.conn.execute("SELECT * FROM constraints_ WHERE project_id=?", (project_id,))}
        p.roles = {r["role_id"]: Role(**dict(r)) for r in self.conn.execute("SELECT * FROM roles WHERE project_id=?", (project_id,))}
        p.facts = {r["fact_id"]: Fact(**dict(r)) for r in self.conn.execute("SELECT * FROM facts WHERE project_id=?", (project_id,))}
        p.assumptions = {r["assumption_id"]: Assumption(**dict(r)) for r in self.conn.execute("SELECT * FROM assumptions WHERE project_id=?", (project_id,))}
        p.preferences = {r["preference_id"]: Preference(**dict(r)) for r in self.conn.execute("SELECT * FROM preferences WHERE project_id=?", (project_id,))}
        p.decisions = {r["decision_id"]: Decision(**dict(r)) for r in self.conn.execute("SELECT * FROM decisions WHERE project_id=?", (project_id,))}
        p.human_reviews = {r["review_id"]: HumanReview(**dict(r)) for r in self.conn.execute("SELECT * FROM human_reviews WHERE project_id=?", (project_id,))}
        p.alternatives = {r["id"]: Alternative(r["id"], r["project_id"], r["name"], r["description"], json.loads(r["parameters_json"]), r["status"], r["version"], r["source"]) for r in self.conn.execute("SELECT * FROM alternatives WHERE project_id=?", (project_id,))}
        p.evaluations = {r["id"]: Evaluation(r["id"], r["alternative_id"], r["objective_id"], r["value"], r["unit"], r["confidence"], r["source"], r["version"]) for r in self.conn.execute("SELECT e.* FROM evaluations e JOIN alternatives a ON a.id=e.alternative_id WHERE a.project_id=?", (project_id,))}
        p.comparisons = {r["id"]: Comparison(r["id"], r["project_id"], json.loads(r["alternative_ids_json"]), [p.evaluations[eid] for eid in json.loads(r["evaluations_json"])], json.loads(r["tradeoffs_json"]), r["version"]) for r in self.conn.execute("SELECT * FROM comparisons WHERE project_id=?", (project_id,))}
        p.recommendations = {r["id"]: Recommendation(r["id"], r["comparison_id"], r["recommended_alternative_id"], r["reason"], r["confidence"], r["status"], r["version"]) for r in self.conn.execute("SELECT r.* FROM recommendations r JOIN comparisons c ON c.id=r.comparison_id WHERE c.project_id=?", (project_id,))}
        p.sources = {r["source_id"]: Source(r["source_id"], r["project_id"], SourceType(r["source_type"]), r["title"], r["url"], r["version"]) for r in self.conn.execute("SELECT * FROM sources WHERE project_id=?", (project_id,))}
        p.evidence = {r["evidence_id"]: Evidence(r["evidence_id"], r["project_id"], r["source_id"], r["statement"], EvidenceType(r["evidence_type"]), datetime.fromisoformat(r["captured_at"]), r["method_version"], r["evidence_url"], r["evidence_hash"], r["state"], r["version"]) for r in self.conn.execute("SELECT * FROM evidence WHERE project_id=?", (project_id,))}
        p.simulations = {r["simulation_id"]: Simulation(r["simulation_id"], r["project_id"], SimulationType(r["simulation_type"]), r["method"], r["method_version"], json.loads(r["inputs_json"]), json.loads(r["outputs_json"]), SimulationState(r["state"]), datetime.fromisoformat(r["started_at"]), datetime.fromisoformat(r["finished_at"]) if r["finished_at"] else None, r["evidence_hash"], r["version"]) for r in self.conn.execute("SELECT * FROM simulations WHERE project_id=?", (project_id,))}
        return p

    def list_projects(self) -> list[Project]:
        return [self.get_project(r["project_id"]) for r in self.conn.execute("SELECT project_id FROM projects ORDER BY project_id")]

    def insert_project(self, project: Project, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO projects(project_id, name, stage, version, spatial_scope, temporal_scope) VALUES (?, ?, ?, ?, ?, ?)",
                (project.project_id, project.name, project.stage, project.version, project.spatial_scope.value if project.spatial_scope else None, project.temporal_scope.value),
            )
            self.add_event(event)

    def update_project_and_event(self, project: Project, event: Event, sql: str, params: tuple) -> None:
        with self.transaction():
            self.conn.execute(sql, params)
            self.conn.execute("UPDATE projects SET version=? WHERE project_id=?", (project.version, project.project_id))
            self.add_event(event)

    def insert_entity_and_event(self, sql: str, params: tuple, project: Project, event: Event) -> None:
        with self.transaction():
            self.conn.execute(sql, params)
            self.conn.execute("UPDATE projects SET version=? WHERE project_id=?", (project.version, project.project_id))
            self.add_event(event)

    def insert_evidence_and_event(self, evidence: Evidence, project: Project, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO evidence(evidence_id, project_id, source_id, statement, evidence_type, captured_at, method_version, evidence_url, evidence_hash, state, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (evidence.evidence_id, evidence.project_id, evidence.source_id, evidence.statement, evidence.evidence_type.value, evidence.captured_at.isoformat(), evidence.method_version, evidence.evidence_url, evidence.evidence_hash, evidence.state, evidence.version),
            )
            self.conn.execute("UPDATE projects SET version=? WHERE project_id=?", (project.version, project.project_id))
            self.add_event(event)

    def list_evidence(self, project_id: str) -> list[Evidence]:
        project = self.get_project(project_id)
        return list(project.evidence.values()) if project else []

    def get_evidence(self, project_id: str, evidence_id: str) -> Evidence | None:
        row = self.conn.execute("SELECT * FROM evidence WHERE project_id=? AND evidence_id=?", (project_id, evidence_id)).fetchone()
        if not row:
            return None
        return Evidence(row["evidence_id"], row["project_id"], row["source_id"], row["statement"], EvidenceType(row["evidence_type"]), datetime.fromisoformat(row["captured_at"]), row["method_version"], row["evidence_url"], row["evidence_hash"], row["state"], row["version"])

    def insert_simulation_and_event(self, simulation: Simulation, project: Project, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO simulations(simulation_id, project_id, simulation_type, method, method_version, inputs_json, outputs_json, state, started_at, finished_at, evidence_hash, version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (simulation.simulation_id, simulation.project_id, simulation.simulation_type.value, simulation.method, simulation.method_version, json.dumps(simulation.inputs, sort_keys=True), json.dumps(simulation.outputs, sort_keys=True), simulation.state.value, simulation.started_at.isoformat(), simulation.finished_at.isoformat() if simulation.finished_at else None, simulation.evidence_hash, simulation.version),
            )
            self.conn.execute("UPDATE projects SET version=? WHERE project_id=?", (project.version, project.project_id))
            self.add_event(event)

    def list_simulations(self, project_id: str) -> list[Simulation]:
        project = self.get_project(project_id)
        return list(project.simulations.values()) if project else []

    def get_simulation(self, project_id: str, simulation_id: str) -> Simulation | None:
        return next((item for item in self.list_simulations(project_id) if item.simulation_id == simulation_id), None)

    def save(self, project: Project) -> None:
        """Persist current state only; events are never replaced or deleted."""
        with self.transaction():
            self.conn.execute(
                "UPDATE projects SET name=?, stage=?, version=?, spatial_scope=?, temporal_scope=? WHERE project_id=?",
                (project.name, project.stage, project.version, project.spatial_scope.value if project.spatial_scope else None, project.temporal_scope.value, project.project_id),
            )
