from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Iterator

from .domain import Assumption, Constraint, Decision, Evidence, EvidenceType, Event, GeneratedAlternative, GenerationMethod, GenerationState, InstitutionalMemory, MemoryConfidence, MemoryState, MemoryType, Fact, HumanReview, InterpretationConfidence, InterpretationState, MultiobjectiveResult, MultiobjectiveState, NormativeInterpretation, NormativeSnapshot, NormativeSnapshotState, Objective, PlanningInstrument, PlanningInstrumentStatus, PlanningInstrumentType, Preference, Project, Regulation, RegulationStatus, Role, ScaleRelation, ScaleRelationType, Source, SourceType, SpatialScope, TemporalScope
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
          key TEXT NOT NULL, direction TEXT NOT NULL, value TEXT NOT NULL, version INTEGER NOT NULL,
          source_parent_objective_id TEXT NULL
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
        CREATE TRIGGER IF NOT EXISTS evaluations_no_update
        BEFORE UPDATE ON evaluations
        BEGIN SELECT RAISE(ABORT, 'evaluations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS evaluations_no_delete
        BEFORE DELETE ON evaluations
        BEGIN SELECT RAISE(ABORT, 'evaluations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS comparisons_no_update
        BEFORE UPDATE ON comparisons
        BEGIN SELECT RAISE(ABORT, 'comparisons are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS comparisons_no_delete
        BEFORE DELETE ON comparisons
        BEGIN SELECT RAISE(ABORT, 'comparisons are append-only'); END;
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
        CREATE TABLE IF NOT EXISTS multiobjective_results (
          multiobjective_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          method TEXT NOT NULL, method_version TEXT NOT NULL, objectives_json TEXT NOT NULL,
          alternatives_json TEXT NOT NULL, pareto_front_json TEXT NOT NULL, dominated_json TEXT NOT NULL,
          incomplete_json TEXT NOT NULL, tradeoffs_json TEXT NOT NULL, state TEXT NOT NULL,
          inputs_hash TEXT NOT NULL, created_at TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TRIGGER IF NOT EXISTS multiobjective_results_no_update
        BEFORE UPDATE ON multiobjective_results
        BEGIN SELECT RAISE(ABORT, 'multiobjective results are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS multiobjective_results_no_delete
        BEFORE DELETE ON multiobjective_results
        BEGIN SELECT RAISE(ABORT, 'multiobjective results are append-only'); END;
        CREATE TABLE IF NOT EXISTS generated_alternatives (
          generation_id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(project_id),
          generator TEXT NOT NULL, generator_version TEXT NOT NULL, method TEXT NOT NULL,
          inputs_json TEXT NOT NULL, candidates_json TEXT NOT NULL, rationale TEXT NOT NULL,
          state TEXT NOT NULL, generation_hash TEXT NOT NULL, created_at TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TRIGGER IF NOT EXISTS generated_alternatives_no_update
        BEFORE UPDATE ON generated_alternatives
        BEGIN SELECT RAISE(ABORT, 'generated alternatives are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS generated_alternatives_no_delete
        BEFORE DELETE ON generated_alternatives
        BEGIN SELECT RAISE(ABORT, 'generated alternatives are append-only'); END;
        CREATE TABLE IF NOT EXISTS institutional_memory (
          memory_id TEXT NOT NULL, version INTEGER NOT NULL,
          memory_type TEXT NOT NULL, scope_json TEXT NOT NULL, project_id_source TEXT NULL,
          summary TEXT NOT NULL, evidence_json TEXT NOT NULL, decisions_json TEXT NOT NULL,
          state TEXT NOT NULL, confidence TEXT NOT NULL, anonymized INTEGER NOT NULL,
          created_at TEXT NOT NULL, PRIMARY KEY(memory_id, version)
        );
        CREATE TRIGGER IF NOT EXISTS institutional_memory_no_update
        BEFORE UPDATE ON institutional_memory
        BEGIN SELECT RAISE(ABORT, 'institutional memory is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS institutional_memory_no_delete
        BEFORE DELETE ON institutional_memory
        BEGIN SELECT RAISE(ABORT, 'institutional memory is append-only'); END;
        CREATE TABLE IF NOT EXISTS planning_instruments (
          instrument_id TEXT PRIMARY KEY, project_id TEXT NULL REFERENCES projects(project_id),
          instrument_type TEXT NOT NULL, name TEXT NOT NULL, jurisdiction TEXT NOT NULL,
          authority TEXT NULL, approval_date TEXT NULL, validity_period TEXT NULL,
          scope_applicable_json TEXT NOT NULL, status TEXT NOT NULL, objectives_json TEXT NOT NULL,
          url TEXT NULL, summary TEXT NULL, source TEXT NOT NULL, version INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS project_planning_instruments (
          project_id TEXT NOT NULL REFERENCES projects(project_id), instrument_id TEXT NOT NULL REFERENCES planning_instruments(instrument_id),
          linked_at TEXT NOT NULL, actor TEXT NOT NULL, PRIMARY KEY(project_id, instrument_id)
        );
        CREATE TRIGGER IF NOT EXISTS planning_instruments_no_update
        BEFORE UPDATE ON planning_instruments
        BEGIN SELECT RAISE(ABORT, 'planning instruments are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS planning_instruments_no_delete
        BEFORE DELETE ON planning_instruments
        BEGIN SELECT RAISE(ABORT, 'planning instruments are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS project_planning_no_update
        BEFORE UPDATE ON project_planning_instruments
        BEGIN SELECT RAISE(ABORT, 'planning links are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS project_planning_no_delete
        BEFORE DELETE ON project_planning_instruments
        BEGIN SELECT RAISE(ABORT, 'planning links are append-only'); END;
        CREATE TABLE IF NOT EXISTS regulations (
          regulation_id TEXT NOT NULL, version_field INTEGER NOT NULL, jurisdiction TEXT NOT NULL,
          authority TEXT NOT NULL, code TEXT NOT NULL, title TEXT NOT NULL, version TEXT NOT NULL,
          publication_date TEXT NULL, effective_date TEXT NULL, status TEXT NOT NULL,
          source_url TEXT NULL, source_type TEXT NOT NULL, evidence_hash TEXT NULL,
          scope_applicable_json TEXT NOT NULL, parent_regulation_id TEXT NULL, summary TEXT NULL,
          PRIMARY KEY(regulation_id, version_field)
        );
        CREATE TABLE IF NOT EXISTS normative_interpretations (
          interpretation_id TEXT NOT NULL, version INTEGER NOT NULL, regulation_id TEXT NOT NULL,
          article_reference TEXT NOT NULL, interpretation_text TEXT NOT NULL, applied_to_project_id TEXT NULL,
          interpreted_by TEXT NOT NULL, interpretation_date TEXT NOT NULL, confidence TEXT NOT NULL,
          state TEXT NOT NULL, disclaimer TEXT NOT NULL, PRIMARY KEY(interpretation_id, version)
        );
        CREATE TABLE IF NOT EXISTS normative_snapshots (
          snapshot_id TEXT NOT NULL, version INTEGER NOT NULL, project_id TEXT NOT NULL REFERENCES projects(project_id),
          cut_date TEXT NOT NULL, jurisdiction TEXT NOT NULL, regulations_included_json TEXT NOT NULL,
          interpretations_included_json TEXT NOT NULL, state TEXT NOT NULL, reviewer TEXT NULL,
          created_at TEXT NOT NULL, PRIMARY KEY(snapshot_id, version)
        );
        CREATE TABLE IF NOT EXISTS scale_relations (
          relation_id TEXT NOT NULL, version INTEGER NOT NULL,
          parent_project_id TEXT NOT NULL REFERENCES projects(project_id),
          child_project_id TEXT NOT NULL REFERENCES projects(project_id),
          relation_type TEXT NOT NULL, description TEXT NULL,
          created_by TEXT NOT NULL, created_at TEXT NOT NULL,
          PRIMARY KEY(relation_id, version)
        );
        CREATE TRIGGER IF NOT EXISTS scale_relations_no_update
        BEFORE UPDATE ON scale_relations
        BEGIN SELECT RAISE(ABORT, 'scale relations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS scale_relations_no_delete
        BEFORE DELETE ON scale_relations
        BEGIN SELECT RAISE(ABORT, 'scale relations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS regulations_no_update
        BEFORE UPDATE ON regulations
        BEGIN SELECT RAISE(ABORT, 'regulations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS regulations_no_delete
        BEFORE DELETE ON regulations
        BEGIN SELECT RAISE(ABORT, 'regulations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS interpretations_no_update
        BEFORE UPDATE ON normative_interpretations
        BEGIN SELECT RAISE(ABORT, 'interpretations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS interpretations_no_delete
        BEFORE DELETE ON normative_interpretations
        BEGIN SELECT RAISE(ABORT, 'interpretations are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS snapshots_no_update
        BEFORE UPDATE ON normative_snapshots
        BEGIN SELECT RAISE(ABORT, 'normative snapshots are append-only'); END;
        CREATE TRIGGER IF NOT EXISTS snapshots_no_delete
        BEFORE DELETE ON normative_snapshots
        BEGIN SELECT RAISE(ABORT, 'normative snapshots are append-only'); END;
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
        objective_columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(objectives)")}
        if "source_parent_objective_id" not in objective_columns:
            self.conn.execute("ALTER TABLE objectives ADD COLUMN source_parent_objective_id TEXT NULL")
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

    @staticmethod
    def _planning_from_row(row: sqlite3.Row) -> PlanningInstrument:
        from datetime import date
        return PlanningInstrument(
            row["instrument_id"], row["project_id"], PlanningInstrumentType(row["instrument_type"]),
            row["name"], row["jurisdiction"], row["authority"],
            date.fromisoformat(row["approval_date"]) if row["approval_date"] else None,
            row["validity_period"], [SpatialScope(value) for value in json.loads(row["scope_applicable_json"])],
            PlanningInstrumentStatus(row["status"]), json.loads(row["objectives_json"]), row["url"],
            row["summary"], row["source"], row["version"],
        )

    @staticmethod
    def _regulation_from_row(row: sqlite3.Row) -> Regulation:
        from datetime import date
        return Regulation(row["regulation_id"], row["jurisdiction"], row["authority"], row["code"], row["title"], row["version"], date.fromisoformat(row["publication_date"]) if row["publication_date"] else None, date.fromisoformat(row["effective_date"]) if row["effective_date"] else None, RegulationStatus(row["status"]), row["source_url"], SourceType(row["source_type"]), row["evidence_hash"], [SpatialScope(value) for value in json.loads(row["scope_applicable_json"])], row["parent_regulation_id"], row["summary"], row["version_field"])

    @staticmethod
    def _interpretation_from_row(row: sqlite3.Row) -> NormativeInterpretation:
        from datetime import date
        return NormativeInterpretation(row["interpretation_id"], row["regulation_id"], row["article_reference"], row["interpretation_text"], row["applied_to_project_id"], row["interpreted_by"], date.fromisoformat(row["interpretation_date"]), InterpretationConfidence(row["confidence"]), InterpretationState(row["state"]), row["disclaimer"], row["version"])

    @staticmethod
    def _snapshot_from_row(row: sqlite3.Row) -> NormativeSnapshot:
        return NormativeSnapshot(row["snapshot_id"], row["project_id"], date.fromisoformat(row["cut_date"]), row["jurisdiction"], json.loads(row["regulations_included_json"]), json.loads(row["interpretations_included_json"]), NormativeSnapshotState(row["state"]), row["reviewer"], datetime.fromisoformat(row["created_at"]), row["version"])

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
        p.multiobjective_results = {r["multiobjective_id"]: MultiobjectiveResult(r["multiobjective_id"], r["project_id"], r["method"], r["method_version"], json.loads(r["objectives_json"]), json.loads(r["alternatives_json"]), json.loads(r["pareto_front_json"]), json.loads(r["dominated_json"]), json.loads(r["incomplete_json"]), json.loads(r["tradeoffs_json"]), MultiobjectiveState(r["state"]), r["inputs_hash"], datetime.fromisoformat(r["created_at"]), r["version"]) for r in self.conn.execute("SELECT * FROM multiobjective_results WHERE project_id=?", (project_id,))}
        p.generated_alternatives = {r["generation_id"]: GeneratedAlternative(r["generation_id"], r["project_id"], r["generator"], r["generator_version"], GenerationMethod(r["method"]), json.loads(r["inputs_json"]), json.loads(r["candidates_json"]), r["rationale"], GenerationState(r["state"]), r["generation_hash"], datetime.fromisoformat(r["created_at"]), r["version"]) for r in self.conn.execute("SELECT * FROM generated_alternatives WHERE project_id=?", (project_id,))}
        p.planning_instruments = {item.instrument_id: item for item in self.list_project_planning_instruments(project_id)}
        p.normative_snapshots = {item.snapshot_id: item for item in self.list_normative_snapshots(project_id)}
        p.scale_relations = {item.relation_id: item for item in self.list_scale_relations(project_id)}
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

    def insert_multiobjective_and_event(self, result: MultiobjectiveResult, project: Project, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO multiobjective_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (result.multiobjective_id, result.project_id, result.method, result.method_version,
                 json.dumps(result.objectives, sort_keys=True), json.dumps(result.alternatives, sort_keys=True),
                 json.dumps(result.pareto_front, sort_keys=True), json.dumps(result.dominated, sort_keys=True),
                 json.dumps(result.incomplete, sort_keys=True), json.dumps(result.tradeoffs, sort_keys=True),
                 result.state.value, result.inputs_hash, result.created_at.isoformat(), result.version),
            )
            self.conn.execute("UPDATE projects SET version=? WHERE project_id=?", (project.version, project.project_id))
            self.add_event(event)

    def list_multiobjective_results(self, project_id: str) -> list[MultiobjectiveResult]:
        project = self.get_project(project_id)
        return list(project.multiobjective_results.values()) if project else []

    def get_multiobjective_result(self, project_id: str, result_id: str) -> MultiobjectiveResult | None:
        project = self.get_project(project_id)
        return project.multiobjective_results.get(result_id) if project else None

    def insert_generation_and_event(self, generation: GeneratedAlternative, project: Project, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO generated_alternatives VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (generation.generation_id, generation.project_id, generation.generator, generation.generator_version,
                 generation.method.value, json.dumps(generation.inputs, sort_keys=True), json.dumps(generation.candidates, sort_keys=True),
                 generation.rationale, generation.state.value, generation.generation_hash, generation.created_at.isoformat(), generation.version),
            )
            self.conn.execute("UPDATE projects SET version=? WHERE project_id=?", (project.version, project.project_id))
            self.add_event(event)

    def list_generations(self, project_id: str) -> list[GeneratedAlternative]:
        project = self.get_project(project_id)
        return list(project.generated_alternatives.values()) if project else []

    def get_generation(self, project_id: str, generation_id: str) -> GeneratedAlternative | None:
        project = self.get_project(project_id)
        return project.generated_alternatives.get(generation_id) if project else None

    def insert_memory_and_event(self, memory: InstitutionalMemory, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO institutional_memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (memory.memory_id, memory.version, memory.memory_type.value, json.dumps([item.value for item in memory.scope]),
                 memory.project_id_source, memory.summary, json.dumps(memory.evidence), json.dumps(memory.decisions_referenced),
                 memory.state.value, memory.confidence.value, int(memory.anonymized), memory.created_at.isoformat()),
            )
            self.add_event(event)

    def list_memory(self) -> list[InstitutionalMemory]:
        rows = self.conn.execute("SELECT m.* FROM institutional_memory m JOIN (SELECT memory_id, MAX(version) version FROM institutional_memory GROUP BY memory_id) latest ON latest.memory_id=m.memory_id AND latest.version=m.version ORDER BY m.created_at, m.memory_id").fetchall()
        return [self._memory_from_row(row) for row in rows]

    def get_memory(self, memory_id: str) -> InstitutionalMemory | None:
        row = self.conn.execute("SELECT * FROM institutional_memory WHERE memory_id=? ORDER BY version DESC LIMIT 1", (memory_id,)).fetchone()
        return self._memory_from_row(row) if row else None

    def revoke_memory_and_event(self, memory: InstitutionalMemory, event: Event) -> InstitutionalMemory:
        revoked = InstitutionalMemory(memory.memory_id, memory.memory_type, memory.scope, memory.project_id_source, memory.summary, memory.evidence, memory.decisions_referenced, MemoryState.REVOKED, memory.confidence, memory.anonymized, datetime.now(), memory.version + 1)
        with self.transaction():
            self.conn.execute(
                "INSERT INTO institutional_memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (revoked.memory_id, revoked.version, revoked.memory_type.value, json.dumps([item.value for item in revoked.scope]), revoked.project_id_source, revoked.summary, json.dumps(revoked.evidence), json.dumps(revoked.decisions_referenced), revoked.state.value, revoked.confidence.value, int(revoked.anonymized), revoked.created_at.isoformat()),
            )
            self.add_event(event)
        return revoked

    @staticmethod
    def _memory_from_row(row: sqlite3.Row) -> InstitutionalMemory:
        return InstitutionalMemory(row["memory_id"], MemoryType(row["memory_type"]), [SpatialScope(item) for item in json.loads(row["scope_json"])], row["project_id_source"], row["summary"], json.loads(row["evidence_json"]), json.loads(row["decisions_json"]), MemoryState(row["state"]), MemoryConfidence(row["confidence"]), bool(row["anonymized"]), datetime.fromisoformat(row["created_at"]), row["version"])

    def insert_planning_instrument_and_event(self, instrument: PlanningInstrument, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO planning_instruments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (instrument.instrument_id, instrument.project_id, instrument.instrument_type.value, instrument.name,
                 instrument.jurisdiction, instrument.authority, instrument.approval_date.isoformat() if instrument.approval_date else None,
                 instrument.validity_period, json.dumps([item.value for item in instrument.scope_applicable]),
                 instrument.status.value, json.dumps(instrument.objectives, sort_keys=True), instrument.url,
                 instrument.summary, instrument.source, instrument.version),
            )
            if event.project_id:
                self.conn.execute("UPDATE projects SET version=version+1 WHERE project_id=?", (event.project_id,))
            self.add_event(event)

    def link_planning_instrument_and_event(self, project: Project, instrument_id: str, actor: str, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO project_planning_instruments(project_id, instrument_id, linked_at, actor) VALUES (?, ?, ?, ?)",
                (project.project_id, instrument_id, event.timestamp, actor),
            )
            self.conn.execute("UPDATE projects SET version=? WHERE project_id=?", (project.version, project.project_id))
            self.add_event(event)

    def list_planning_instruments(self, instrument_type: str | None = None, jurisdiction: str | None = None, scope_applicable: str | None = None) -> list[PlanningInstrument]:
        query = "SELECT * FROM planning_instruments WHERE 1=1"
        params: list[str] = []
        if instrument_type:
            query += " AND instrument_type=?"
            params.append(instrument_type)
        if jurisdiction:
            query += " AND jurisdiction=?"
            params.append(jurisdiction)
        rows = self.conn.execute(query + " ORDER BY instrument_id", params).fetchall()
        values = [self._planning_from_row(row) for row in rows]
        if scope_applicable:
            values = [item for item in values if scope_applicable in {scope.value for scope in item.scope_applicable}]
        return values

    def get_planning_instrument(self, instrument_id: str) -> PlanningInstrument | None:
        row = self.conn.execute("SELECT * FROM planning_instruments WHERE instrument_id=?", (instrument_id,)).fetchone()
        return self._planning_from_row(row) if row else None

    def list_project_planning_instruments(self, project_id: str) -> list[PlanningInstrument]:
        rows = self.conn.execute(
            "SELECT p.* FROM planning_instruments p JOIN project_planning_instruments l ON l.instrument_id=p.instrument_id WHERE l.project_id=? ORDER BY p.instrument_id",
            (project_id,),
        ).fetchall()
        return [self._planning_from_row(row) for row in rows]

    def insert_regulation_and_event(self, regulation: Regulation, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO regulations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (regulation.regulation_id, regulation.version_field, regulation.jurisdiction, regulation.authority, regulation.code, regulation.title, regulation.version,
                 regulation.publication_date.isoformat() if regulation.publication_date else None, regulation.effective_date.isoformat() if regulation.effective_date else None,
                 regulation.status.value, regulation.source_url, regulation.source_type.value, regulation.evidence_hash,
                 json.dumps([item.value for item in regulation.scope_applicable]), regulation.parent_regulation_id, regulation.summary),
            )
            self.conn.execute("UPDATE projects SET version=version+1 WHERE project_id=?", (event.project_id,))
            self.add_event(event)

    def list_regulations(self) -> list[Regulation]:
        rows = self.conn.execute("SELECT r.* FROM regulations r WHERE NOT EXISTS (SELECT 1 FROM regulations newer WHERE newer.regulation_id=r.regulation_id AND newer.version_field>r.version_field) ORDER BY r.regulation_id").fetchall()
        return [self._regulation_from_row(row) for row in rows]

    def get_regulation(self, regulation_id: str) -> Regulation | None:
        row = self.conn.execute("SELECT r.* FROM regulations r WHERE r.regulation_id=? AND NOT EXISTS (SELECT 1 FROM regulations newer WHERE newer.regulation_id=r.regulation_id AND newer.version_field>r.version_field)", (regulation_id,)).fetchone()
        return self._regulation_from_row(row) if row else None

    def insert_interpretation_and_event(self, interpretation: NormativeInterpretation, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO normative_interpretations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (interpretation.interpretation_id, interpretation.version, interpretation.regulation_id, interpretation.article_reference, interpretation.interpretation_text,
                 interpretation.applied_to_project_id, interpretation.interpreted_by, interpretation.interpretation_date.isoformat(), interpretation.confidence.value,
                 interpretation.state.value, interpretation.disclaimer),
            )
            self.conn.execute("UPDATE projects SET version=version+1 WHERE project_id=?", (event.project_id,))
            self.add_event(event)

    def list_interpretations(self, regulation_id: str | None = None) -> list[NormativeInterpretation]:
        query = "SELECT i.* FROM normative_interpretations i WHERE NOT EXISTS (SELECT 1 FROM normative_interpretations newer WHERE newer.interpretation_id=i.interpretation_id AND newer.version>i.version)"
        params: list[str] = []
        if regulation_id:
            query += " AND i.regulation_id=?"
            params.append(regulation_id)
        rows = self.conn.execute(query + " ORDER BY i.interpretation_id", params).fetchall()
        return [self._interpretation_from_row(row) for row in rows]

    def get_interpretation(self, interpretation_id: str) -> NormativeInterpretation | None:
        row = self.conn.execute("SELECT i.* FROM normative_interpretations i WHERE i.interpretation_id=? AND NOT EXISTS (SELECT 1 FROM normative_interpretations newer WHERE newer.interpretation_id=i.interpretation_id AND newer.version>i.version)", (interpretation_id,)).fetchone()
        return self._interpretation_from_row(row) if row else None

    def insert_snapshot_and_event(self, snapshot: NormativeSnapshot, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO normative_snapshots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (snapshot.snapshot_id, snapshot.version, snapshot.project_id, snapshot.cut_date.isoformat(), snapshot.jurisdiction,
                 json.dumps(snapshot.regulations_included), json.dumps(snapshot.interpretations_included), snapshot.state.value,
                 snapshot.reviewer, snapshot.created_at.isoformat()),
            )
            self.conn.execute("UPDATE projects SET version=version+1 WHERE project_id=?", (snapshot.project_id,))
            self.add_event(event)

    def list_normative_snapshots(self, project_id: str) -> list[NormativeSnapshot]:
        rows = self.conn.execute("SELECT s.* FROM normative_snapshots s WHERE s.project_id=? AND NOT EXISTS (SELECT 1 FROM normative_snapshots newer WHERE newer.snapshot_id=s.snapshot_id AND newer.version>s.version) ORDER BY s.snapshot_id", (project_id,)).fetchall()
        return [self._snapshot_from_row(row) for row in rows]

    def get_normative_snapshot(self, snapshot_id: str) -> NormativeSnapshot | None:
        row = self.conn.execute("SELECT s.* FROM normative_snapshots s WHERE s.snapshot_id=? AND NOT EXISTS (SELECT 1 FROM normative_snapshots newer WHERE newer.snapshot_id=s.snapshot_id AND newer.version>s.version)", (snapshot_id,)).fetchone()
        return self._snapshot_from_row(row) if row else None

    @staticmethod
    def _scale_relation_from_row(row: sqlite3.Row) -> ScaleRelation:
        return ScaleRelation(row["relation_id"], row["parent_project_id"], row["child_project_id"], ScaleRelationType(row["relation_type"]), row["description"], row["created_by"], datetime.fromisoformat(row["created_at"]), row["version"])

    def insert_scale_relation_and_event(self, relation: ScaleRelation, event: Event) -> None:
        with self.transaction():
            self.conn.execute(
                "INSERT INTO scale_relations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (relation.relation_id, relation.version, relation.parent_project_id, relation.child_project_id,
                 relation.relation_type.value, relation.description, relation.created_by, relation.created_at.isoformat()),
            )
            self.conn.execute("UPDATE projects SET version=version+1 WHERE project_id IN (?, ?)", (relation.parent_project_id, relation.child_project_id))
            self.add_event(event)

    def list_scale_relations(self, project_id: str) -> list[ScaleRelation]:
        rows = self.conn.execute(
            "SELECT r.* FROM scale_relations r WHERE (r.parent_project_id=? OR r.child_project_id=?) AND NOT EXISTS (SELECT 1 FROM scale_relations newer WHERE newer.relation_id=r.relation_id AND newer.version>r.version) ORDER BY r.created_at, r.relation_id",
            (project_id, project_id),
        ).fetchall()
        return [self._scale_relation_from_row(row) for row in rows]

    def get_scale_relation(self, relation_id: str) -> ScaleRelation | None:
        row = self.conn.execute("SELECT r.* FROM scale_relations r WHERE r.relation_id=? AND NOT EXISTS (SELECT 1 FROM scale_relations newer WHERE newer.relation_id=r.relation_id AND newer.version>r.version)", (relation_id,)).fetchone()
        return self._scale_relation_from_row(row) if row else None

    def has_scale_relation(self, parent_project_id: str, child_project_id: str, relation_type: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM scale_relations WHERE parent_project_id=? AND child_project_id=? AND relation_type=? LIMIT 1",
            (parent_project_id, child_project_id, relation_type),
        ).fetchone() is not None

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
