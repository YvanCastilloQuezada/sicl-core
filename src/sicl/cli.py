from __future__ import annotations

import shlex
import uuid
import json
import csv
import hashlib
from datetime import date, datetime, timezone
from dataclasses import asdict
from typing import Any

from .domain import Actor, ActorPosition, ActorRole, ActorState, Assumption, AuthorityLevel, Constraint, CycleHorizon, CycleState, Decision, Evidence, EvidenceType, Event, EvolutionState, GeneratedAlternative, GenerationMethod, GenerationState, HumanReview, Fact, InterpretationConfidence, InterpretationState, MemoryState, MultiobjectiveResult, MultiobjectiveState, NormativeInterpretation, NormativeSnapshot, NormativeSnapshotState, Objective, PlanningInstrument, PlanningInstrumentStatus, PlanningInstrumentType, Project, Regulation, RegulationStatus, Role, ScaleRelation, ScaleRelationType, ScenarioBranch, ScenarioEvolution, ScenarioState, SpatialScope, SourceType, Stance, SubjectType, TemporalCycle, TemporalScope, KNOWLEDGE_STATES, DIRECTIONS, STAGES, now_iso
from .repository import SICLError, SQLiteRepository
from .v11 import Alternative, Comparison, Evaluation, Recommendation, EVALUATION_SOURCES
from .export import dashboard_text, export_csv, export_project_json, export_report, report_text, tradeoffs_text
from .site_intelligence import get_site_observation
from .agents import BioclimaticAgent, EconomicAgent, StructuralAgent
from .optimization import GenerativeOptimizer, pareto_front, tradeoff_matrix
from .simulation import METHODS, Simulation, SimulationState, SimulationType, canonical_hash, execute_method, list_methods, now_utc, simulation_to_dict
from .design_principles import get_principle, list_principles
from .regulatory import LEGAL_DISCLAIMER, interpretation_to_dict, regulation_to_dict, snapshot_to_dict
from .multiscale import SCALE_ORDER, children_scopes, is_ancestor, parent_scope
from .generation import generate_candidates, generation_to_dict, list_generation_methods
from .memory import extract_memory, memory_to_dict, memory_types
from .actors import actor_to_dict, position_to_dict
from .temporal import cycle_to_dict, evolution_to_dict, scenario_to_dict
from .feasibility import ProjectVariable, VariableType, evaluate_feasibility, feasible_pareto_front, normalized_key, project_variable_dict, serialize_result, validate_project_variable_uniqueness


class CLI:
    def __init__(self, repository: SQLiteRepository | None = None, actor: str = "human") -> None:
        self.repo = repository or SQLiteRepository()
        self.actor = actor
        self.current_project: str | None = None
        self.closed = False

    def _project(self) -> Project:
        if not self.current_project:
            raise SICLError("PROJECT_NOT_FOUND", "No project is open")
        p = self.repo.get_project(self.current_project)
        if not p:
            raise SICLError("PROJECT_NOT_FOUND", self.current_project)
        return p

    def _event(self, project_id: str, typ: str, payload: dict, source: str = "USER_COMMAND") -> Event:
        payload = {**payload, "actor": self.actor}
        return Event(None, now_iso(), project_id, typ, payload, self.actor, source)

    def execute(self, command: str) -> dict:
        try:
            parts = shlex.split(command)
            if not parts or parts[0] == "/HELP":
                return self._ok({"commands": ["/PROJECT CREATE", "/PROJECT OPEN", "/PROJECT SET SCOPE", "/PROJECT IMPORT OBJECTIVE", "/PROJECT SHOW", "/PROJECT LIST", "/STAGE SET", "/OBJECTIVE SET", "/CONSTRAINT SET", "/ROLE ADD", "/ACTOR ADD", "/ACTOR LIST", "/ACTOR SHOW", "/POSITION ADD", "/POSITION LIST", "/CYCLE CREATE", "/CYCLE LIST", "/CYCLE SHOW", "/SCENARIO CREATE", "/SCENARIO LIST", "/SCENARIO SELECT", "/FACT SET", "/ASSUMPTION SET", "/EVIDENCE ADD", "/EVIDENCE LIST", "/EVIDENCE SHOW", "/HUMAN REVIEW", "/SITE INTELLIGENCE", "/AGENT RUN", "/DEBATE", "/GENERATE DESIGN", "/GENERATE LIST", "/GENERATE SHOW", "/GENERATE METHODS", "/ALTERNATIVE PROMOTE", "/MEMORY LIST", "/MEMORY SHOW", "/MEMORY EXTRACT", "/MEMORY REVOKE", "/MEMORY APPLY", "/MEMORY TYPES", "/GENERATE", "/PARETO", "/TRADEOFF_MATRIX", "/MULTIOBJECTIVE", "/SCALE PARENT", "/SCALE CHILDREN", "/SCALE RELATE", "/SCALE RELATIONS", "/PLANNING ADD", "/PLANNING LIST", "/PLANNING SHOW", "/PLANNING TYPES", "/REGULATION ADD", "/REGULATION LIST", "/REGULATION SHOW", "/REGULATION STATUS", "/INTERPRET ADD", "/INTERPRET LIST", "/INTERPRET REVIEW", "/SNAPSHOT CREATE", "/SNAPSHOT LIST", "/SNAPSHOT FREEZE", "/DECISION RECORD", "/STATUS", "/HISTORY", "/EXIT"]})
            head = tuple(p.upper() for p in parts[:2])
            if head == ("/EXIT",):
                self.closed = True
                return self._ok({"closed": True})
            if head == ("/PROJECT", "CREATE"):
                return self.project_create(parts[2:])
            if head == ("/PROJECT", "IMPORT") and len(parts) > 2 and parts[2].upper() == "OBJECTIVE":
                return self.project_import_objective(parts[3:])
            if head == ("/PROJECT", "SET") and len(parts) > 2 and parts[2].upper() == "SCOPE":
                return self.project_set_scope(parts[3:])
            if head == ("/PROJECT", "OPEN"):
                return self.project_open(parts[2:])
            if head == ("/PROJECT", "SHOW"):
                return self.project_show()
            if head == ("/PROJECT", "LIST"):
                return self._ok({"projects": [asdict(p) for p in self.repo.list_projects()]})
            if head == ("/STAGE", "SET"):
                return self.stage_set(parts[2:])
            if head == ("/SCALE", "PARENT"):
                if len(parts) != 3: raise SICLError("INVALID_ARGUMENT", "scope required")
                try:
                    parent = parent_scope(parts[2])
                except ValueError as exc:
                    raise SICLError("INVALID_SCOPE", f"invalid scope: {parts[2]}") from exc
                return self._ok({"scope": parts[2].lower(), "parent": parent.value if parent else None})
            if head == ("/SCALE", "CHILDREN"):
                if len(parts) != 3: raise SICLError("INVALID_ARGUMENT", "scope required")
                try:
                    children = children_scopes(parts[2])
                except ValueError as exc:
                    raise SICLError("INVALID_SCOPE", f"invalid scope: {parts[2]}") from exc
                return self._ok({"scope": parts[2].lower(), "children": [item.value for item in children]})
            if head == ("/SCALE", "RELATE"):
                return self.scale_relate(parts[2:])
            if head == ("/SCALE", "RELATIONS"):
                return self.scale_relations(parts[2:])
            if head == ("/OBJECTIVE", "SET"):
                return self.objective_set(parts[2:])
            if head == ("/CONSTRAINT", "SET"):
                return self.constraint_set(parts[2:])
            if head == ("/VARIABLE", "ADD"):
                return self.variable_add(parts[2:])
            if head == ("/VARIABLE", "LIST"):
                return self.variable_list()
            if head == ("/FEASIBILITY", "CHECK"):
                return self.feasibility_check(parts[2:])
            if head == ("/ROLE", "ADD"):
                return self.role_add(parts[2:])
            if head == ("/ACTOR", "ADD"):
                return self.actor_add(parts[2:])
            if head == ("/ACTOR", "LIST"):
                return self.actor_list()
            if head == ("/ACTOR", "SHOW"):
                return self.actor_show(parts[2:])
            if head == ("/POSITION", "ADD"):
                return self.position_add(parts[2:])
            if head == ("/POSITION", "LIST"):
                return self.position_list(parts[2:])
            if head == ("/CYCLE", "CREATE"):
                return self.cycle_create(parts[2:])
            if head == ("/CYCLE", "LIST"):
                return self.cycle_list()
            if head == ("/CYCLE", "SHOW"):
                return self.cycle_show(parts[2:])
            if head == ("/SCENARIO", "CREATE"):
                return self.scenario_create(parts[2:])
            if head == ("/SCENARIO", "LIST"):
                return self.scenario_list()
            if head == ("/SCENARIO", "SELECT"):
                return self.scenario_select(parts[2:])
            if head == ("/EVOLUTION", "CREATE"):
                return self.evolution_create(parts[2:])
            if head == ("/EVOLUTION", "ADD"):
                return self.evolution_add(parts[2:])
            if head == ("/EVOLUTION", "APPLY"):
                return self.evolution_apply(parts[2:])
            if head == ("/EVOLUTION", "LIST"):
                return self.evolution_list()
            if head == ("/EVOLUTION", "SHOW"):
                return self.evolution_show(parts[2:])
            if head == ("/FACT", "SET"):
                return self.fact_set(parts[2:])
            if head == ("/ASSUMPTION", "SET"):
                return self.assumption_set(parts[2:])
            if head == ("/EVIDENCE", "ADD"):
                return self.evidence_add(parts[2:])
            if head == ("/EVIDENCE", "LIST"):
                return self.evidence_list()
            if head == ("/EVIDENCE", "SHOW"):
                return self.evidence_show(parts[2:])
            if head == ("/HUMAN", "REVIEW"):
                return self.human_review(parts[2:])
            if head == ("/SITE", "INTELLIGENCE"):
                return self.site_intelligence(" ".join(parts[2:]))
            if head == ("/AGENT", "RUN"):
                return self.agent_run(parts[2:])
            if head == ("/DECISION", "RECORD"):
                return self.decision_record(parts[2:])
            if head == ("/ALTERNATIVE", "CREATE"):
                return self.alternative_create(parts[2:])
            if head == ("/ALTERNATIVE", "SET"):
                return self.alternative_set(parts[2:])
            if head == ("/ALTERNATIVE", "LIST"):
                return self.alternative_list()
            if head == ("/ALTERNATIVE", "PROMOTE"):
                return self.alternative_promote(parts[2:])
            if head == ("/MEMORY", "LIST"):
                return self.memory_list()
            if head == ("/MEMORY", "SHOW"):
                return self.memory_show(parts[2:])
            if head == ("/MEMORY", "EXTRACT"):
                return self.memory_extract(parts[2:])
            if head == ("/MEMORY", "REVOKE"):
                return self.memory_revoke(parts[2:])
            if head == ("/MEMORY", "APPLY"):
                return self.memory_apply(parts[2:])
            if head == ("/MEMORY", "TYPES"):
                return self._ok({"types": memory_types()})
            if parts[0].upper() == "/EVALUATE":
                return self.evaluate(parts[1:])
            if parts[0].upper() == "/COMPARE":
                return self.compare(parts[1:])
            if parts[0].upper() == "/RECOMMEND":
                return self.recommend()
            if parts[0].upper() == "/PARETO":
                return self.pareto(parts[1:])
            if parts[0].upper() == "/DEBATE":
                return self.debate(parts[1:])
            if parts[0].upper() == "/GENERATE":
                if len(parts) > 1 and parts[1].upper() in {"DESIGN", "LIST", "SHOW", "METHODS"}:
                    if parts[1].upper() == "DESIGN":
                        return self.generate_design(parts[2:])
                    if parts[1].upper() == "LIST":
                        return self.generate_list()
                    if parts[1].upper() == "SHOW":
                        return self.generate_show(parts[2:])
                    return self._ok({"methods": list_generation_methods()})
                return self.generate(parts[1:])
            if parts[0].upper() == "/TRADEOFF_MATRIX":
                return self.tradeoff_matrix_command(parts[1:])
            if head == ("/MULTIOBJECTIVE", "PARETO"):
                return self.multiobjective_pareto(parts[2:])
            if head == ("/MULTIOBJECTIVE", "FEASIBLE_PARETO"):
                return self.multiobjective_feasible_pareto(parts[2:])
            if head == ("/MULTIOBJECTIVE", "TRADEOFFS"):
                return self.multiobjective_tradeoffs(parts[2:])
            if head == ("/MULTIOBJECTIVE", "LIST"):
                return self.multiobjective_list()
            if head == ("/MULTIOBJECTIVE", "SHOW"):
                return self.multiobjective_show(parts[2:])
            if head == ("/SIMULATE", "RUN"):
                return self.simulate_run(parts[2:])
            if head == ("/SIMULATE", "MONTE_CARLO"):
                return self.simulate_monte_carlo(parts[2:])
            if head == ("/SIMULATE", "LIST"):
                return self.simulate_list()
            if head == ("/SIMULATE", "SHOW"):
                return self.simulate_show(parts[2:])
            if head == ("/SIMULATE", "METHODS"):
                return self._ok({"methods": list_methods()})
            if head == ("/DESIGN", "PRINCIPLES"):
                return self._ok({"principles": list_principles()})
            if head == ("/DESIGN", "PRINCIPLE"):
                if len(parts) != 3:
                    raise SICLError("INVALID_ARGUMENT", "principle_id required")
                principle = get_principle(parts[2])
                if principle is None:
                    raise SICLError("PRINCIPLE_NOT_FOUND", parts[2])
                return self._ok({"principle": principle})
            if head == ("/PLANNING", "ADD"):
                return self.planning_add(parts[2:])
            if head == ("/PLANNING", "LIST"):
                return self.planning_list()
            if head == ("/PLANNING", "SHOW"):
                return self.planning_show(parts[2:])
            if head == ("/PLANNING", "TYPES"):
                return self._ok({"types": [item.value for item in PlanningInstrumentType]})
            if head == ("/REGULATION", "ADD"):
                return self.regulation_add(parts[2:])
            if head == ("/REGULATION", "LIST"):
                return self.regulation_list()
            if head == ("/REGULATION", "SHOW"):
                return self.regulation_show(parts[2:])
            if head == ("/REGULATION", "STATUS"):
                return self.regulation_status(parts[2:])
            if head == ("/INTERPRET", "ADD"):
                return self.interpret_add(parts[2:])
            if head == ("/INTERPRET", "LIST"):
                return self.interpret_list(parts[2:])
            if head == ("/INTERPRET", "REVIEW"):
                return self.interpret_review(parts[2:])
            if head == ("/SNAPSHOT", "CREATE"):
                return self.snapshot_create(parts[2:])
            if head == ("/SNAPSHOT", "LIST"):
                return self.snapshot_list(parts[2:])
            if head == ("/SNAPSHOT", "FREEZE"):
                return self.snapshot_freeze(parts[2:])
            if parts[0].upper() == "/REPORT":
                return self._text_response(report_text(self.repo, self._project()))
            if parts[0].upper() == "/TRADEOFFS":
                return self._text_response(tradeoffs_text(self._project()))
            if parts[0].upper() == "/DASHBOARD":
                return self._text_response(dashboard_text(self.repo, self._project()))
            if head == ("/EXPORT", "PROJECT"):
                return self.export_project(parts[2:])
            if head == ("/EXPORT", "CSV"):
                return self.export_csv_command(parts[2:])
            if head == ("/EXPORT", "REPORT"):
                return self.export_report_command(parts[2:])
            if head == ("/IMPORT", "CSV"):
                return self.import_csv_command(parts[2:])
            if head == ("/STATUS",) or head == ("/PROJECT", "STATUS"):
                return self._ok(asdict(self._project()))
            if head == ("/HISTORY",):
                return self._ok({"events": [asdict(e) for e in self.repo.events(self.current_project)]})
            raise SICLError("UNKNOWN_COMMAND", command)
        except SICLError as e:
            return {"status": "ERROR", "code": e.code, "message": e.message, "data": {}}

    def _ok(self, data: dict) -> dict:
        return {"status": "OK", "code": "OK", "message": "ok", "data": data}

    def _text_response(self, text: str) -> dict:
        return {"status": "OK", "code": "OK", "message": "ok", "data": {"text": text}}

    def _require_open(self) -> Project:
        p = self._project()
        if p.stage == "CLOSED":
            raise SICLError("INVALID_STATE", "Project is CLOSED")
        return p

    @staticmethod
    def _planning_dict(instrument: PlanningInstrument) -> dict:
        value = asdict(instrument)
        value["instrument_type"] = instrument.instrument_type.value
        value["status"] = instrument.status.value
        value["scope_applicable"] = [scope.value for scope in instrument.scope_applicable]
        value["approval_date"] = instrument.approval_date.isoformat() if instrument.approval_date else None
        return value

    def planning_add(self, args: list[str]) -> dict:
        if len(args) < 3 or len(args) > 5:
            raise SICLError("INVALID_ARGUMENT", "instrument_id instrument_type name [jurisdiction] [url] required")
        project = self._project()
        try:
            instrument_type = PlanningInstrumentType(args[1].upper())
        except ValueError:
            raise SICLError("INVALID_ARGUMENT", "invalid instrument_type")
        instrument_id, name = args[0], args[2]
        if self.repo.get_planning_instrument(instrument_id) is not None:
            raise SICLError("CONFLICT", f"planning instrument already exists: {instrument_id}")
        jurisdiction = args[3] if len(args) >= 4 else "GLOBAL"
        url = args[4] if len(args) >= 5 else None
        instrument = PlanningInstrument(instrument_id, None, instrument_type, name, jurisdiction, None, None, None, [], PlanningInstrumentStatus.ACTIVE if url else PlanningInstrumentStatus.UNKNOWN, [], url, None, url or "PENDING_REFERENCE")
        project.version += 1
        self.repo.insert_planning_instrument_and_event(instrument, self._event(project.project_id, "PLANNING_INSTRUMENT_REGISTERED", self._planning_dict(instrument)))
        return self._ok({"instrument": self._planning_dict(instrument)})

    def planning_list(self) -> dict:
        return self._ok({"instruments": [self._planning_dict(item) for item in self.repo.list_planning_instruments()]})

    def planning_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "instrument_id required")
        instrument = self.repo.get_planning_instrument(args[0])
        if instrument is None:
            raise SICLError("PLANNING_INSTRUMENT_NOT_FOUND", args[0])
        return self._ok({"instrument": self._planning_dict(instrument)})

    def regulation_add(self, args: list[str]) -> dict:
        if len(args) < 3 or len(args) > 5:
            raise SICLError("INVALID_ARGUMENT", "regulation_id code title [jurisdiction] [source_url] required")
        project = self._project()
        regulation_id, code, title = args[:3]
        if self.repo.get_regulation(regulation_id):
            raise SICLError("CONFLICT", f"regulation already exists: {regulation_id}")
        jurisdiction = args[3] if len(args) >= 4 else "UNKNOWN"
        source_url = args[4] if len(args) >= 5 else None
        regulation = Regulation(regulation_id, jurisdiction, "UNKNOWN", code, title, "1.0", None, None, RegulationStatus.NO_VERIFICADA, source_url, SourceType.OFFICIAL if source_url else SourceType.UNKNOWN, None, [], None, None)
        self.repo.insert_regulation_and_event(regulation, self._event(project.project_id, "REGULATION_REGISTERED", regulation_to_dict(regulation)))
        return self._ok({"regulation": regulation_to_dict(regulation)})

    def regulation_list(self) -> dict:
        return self._ok({"regulations": [regulation_to_dict(item) for item in self.repo.list_regulations()]})

    def regulation_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "regulation_id required")
        item = self.repo.get_regulation(args[0])
        if item is None:
            raise SICLError("REGULATION_NOT_FOUND", args[0])
        return self._ok({"regulation": regulation_to_dict(item)})

    def regulation_status(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "regulation_id status required")
        project = self._project()
        current = self.repo.get_regulation(args[0])
        if current is None:
            raise SICLError("REGULATION_NOT_FOUND", args[0])
        try:
            status = RegulationStatus(args[1].upper())
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid regulation status") from exc
        updated = Regulation(current.regulation_id, current.jurisdiction, current.authority, current.code, current.title, current.version, current.publication_date, current.effective_date, status, current.source_url, current.source_type, current.evidence_hash, current.scope_applicable, current.parent_regulation_id, current.summary, current.version_field + 1)
        self.repo.insert_regulation_and_event(updated, self._event(project.project_id, "REGULATION_STATUS_CHANGED", regulation_to_dict(updated)))
        return self._ok({"regulation": regulation_to_dict(updated)})

    def interpret_add(self, args: list[str]) -> dict:
        if len(args) != 4:
            raise SICLError("INVALID_ARGUMENT", "interpretation_id regulation_id article_reference interpretation_text required")
        project = self._project()
        if self.repo.get_regulation(args[1]) is None:
            raise SICLError("REGULATION_NOT_FOUND", args[1])
        if self.repo.get_interpretation(args[0]):
            raise SICLError("CONFLICT", f"interpretation already exists: {args[0]}")
        item = NormativeInterpretation(args[0], args[1], args[2], args[3], None, self.actor, date.today(), InterpretationConfidence.UNKNOWN, InterpretationState.DRAFT, LEGAL_DISCLAIMER)
        self.repo.insert_interpretation_and_event(item, self._event(project.project_id, "NORMATIVE_INTERPRETATION_REGISTERED", interpretation_to_dict(item)))
        return self._ok({"interpretation": interpretation_to_dict(item)})

    def interpret_list(self, args: list[str]) -> dict:
        if len(args) > 1:
            raise SICLError("INVALID_ARGUMENT", "optional regulation_id only")
        return self._ok({"interpretations": [interpretation_to_dict(item) for item in self.repo.list_interpretations(args[0] if args else None)]})

    def interpret_review(self, args: list[str]) -> dict:
        if len(args) != 3:
            raise SICLError("INVALID_ARGUMENT", "interpretation_id actor authority required")
        project = self._project()
        current = self.repo.get_interpretation(args[0])
        if current is None:
            raise SICLError("INTERPRETATION_NOT_FOUND", args[0])
        if not args[1] or not args[2]:
            raise SICLError("INVALID_ARGUMENT", "actor and authority required")
        reviewed = NormativeInterpretation(current.interpretation_id, current.regulation_id, current.article_reference, current.interpretation_text, current.applied_to_project_id, args[1], current.interpretation_date, current.confidence, InterpretationState.REVIEWED, LEGAL_DISCLAIMER, current.version + 1)
        self.repo.insert_interpretation_and_event(reviewed, self._event(project.project_id, "NORMATIVE_INTERPRETATION_REVIEWED", {**interpretation_to_dict(reviewed), "authority": args[2]}))
        return self._ok({"interpretation": interpretation_to_dict(reviewed), "authority": args[2], "applicable": True})

    def snapshot_create(self, args: list[str]) -> dict:
        if len(args) != 3:
            raise SICLError("INVALID_ARGUMENT", "snapshot_id project_id cut_date required")
        project = self.repo.get_project(args[1])
        if project is None:
            raise SICLError("PROJECT_NOT_FOUND", args[1])
        try:
            cut_date = date.fromisoformat(args[2])
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "cut_date must be YYYY-MM-DD") from exc
        if self.repo.get_normative_snapshot(args[0]):
            raise SICLError("CONFLICT", f"snapshot already exists: {args[0]}")
        item = NormativeSnapshot(args[0], args[1], cut_date, "UNKNOWN", [r.regulation_id for r in self.repo.list_regulations()], [i.interpretation_id for i in self.repo.list_interpretations()], NormativeSnapshotState.DRAFT, None, datetime.now(timezone.utc))
        self.repo.insert_snapshot_and_event(item, self._event(args[1], "NORMATIVE_SNAPSHOT_CREATED", snapshot_to_dict(item)))
        return self._ok({"snapshot": snapshot_to_dict(item)})

    def snapshot_list(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "project_id required")
        if self.repo.get_project(args[0]) is None:
            raise SICLError("PROJECT_NOT_FOUND", args[0])
        return self._ok({"snapshots": [snapshot_to_dict(item) for item in self.repo.list_normative_snapshots(args[0])]})

    def snapshot_freeze(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "snapshot_id reviewer required")
        current = self.repo.get_normative_snapshot(args[0])
        if current is None:
            raise SICLError("SNAPSHOT_NOT_FOUND", args[0])
        if current.state == NormativeSnapshotState.FROZEN:
            raise SICLError("INVALID_STATE", "FROZEN snapshot is immutable")
        frozen = NormativeSnapshot(current.snapshot_id, current.project_id, current.cut_date, current.jurisdiction, current.regulations_included, current.interpretations_included, NormativeSnapshotState.FROZEN, args[1], current.created_at, current.version + 1)
        self.repo.insert_snapshot_and_event(frozen, self._event(current.project_id, "NORMATIVE_SNAPSHOT_FROZEN", snapshot_to_dict(frozen)))
        return self._ok({"snapshot": snapshot_to_dict(frozen)})

    def scale_relate(self, args: list[str]) -> dict:
        if len(args) not in (3, 4):
            raise SICLError("INVALID_ARGUMENT", "parent_project_id child_project_id relation_type [description] required")
        parent_id, child_id = args[:2]
        if parent_id == child_id:
            raise SICLError("INVALID_ARGUMENT", "a project cannot relate to itself")
        parent = self.repo.get_project(parent_id)
        child = self.repo.get_project(child_id)
        if parent is None or child is None:
            raise SICLError("PROJECT_NOT_FOUND", parent_id if parent is None else child_id)
        try:
            relation_type = ScaleRelationType(args[2].upper())
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid relation_type") from exc
        if self.repo.has_scale_relation(parent_id, child_id, relation_type.value):
            raise SICLError("CONFLICT", "scale relation already exists")
        if relation_type == ScaleRelationType.CONTAINS and (parent.spatial_scope is None or child.spatial_scope is None or not is_ancestor(parent.spatial_scope, child.spatial_scope)):
            raise SICLError("INVALID_SCOPE_RELATION", "CONTAINS requires an explicit ancestor spatial scope")
        relation = ScaleRelation(f"REL-{uuid.uuid4().hex[:10]}", parent_id, child_id, relation_type, args[3] if len(args) == 4 else None, self.actor, datetime.now(timezone.utc), 1)
        event_payload = {**asdict(relation), "relation_type": relation.relation_type.value, "created_at": relation.created_at.isoformat()}
        event = self._event(parent_id, "SCALE_RELATION_CREATED", event_payload)
        self.repo.insert_scale_relation_and_event(relation, event)
        return self._ok(asdict(relation))

    def scale_relations(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "project_id required")
        if self.repo.get_project(args[0]) is None:
            raise SICLError("PROJECT_NOT_FOUND", args[0])
        return self._ok({"relations": [asdict(item) for item in self.repo.list_scale_relations(args[0])]})

    def project_import_objective(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "source_project_id objective_id required")
        child = self._require_open()
        source_project = self.repo.get_project(args[0])
        if source_project is None:
            raise SICLError("PROJECT_NOT_FOUND", args[0])
        objective = source_project.objectives.get(args[1])
        if objective is None:
            raise SICLError("OBJECTIVE_NOT_FOUND", args[1])
        relation = next((item for item in self.repo.list_scale_relations(child.project_id) if item.parent_project_id == source_project.project_id and item.child_project_id == child.project_id and item.relation_type == ScaleRelationType.CONTAINS), None)
        if relation is None:
            raise SICLError("SCALE_RELATION_REQUIRED", "source project must contain the current project")
        imported_id = f"OBJ-{uuid.uuid4().hex[:10]}"
        imported = Objective(imported_id, child.project_id, objective.key, objective.direction, objective.value, 1, objective.objective_id)
        child.objectives[imported_id] = imported
        child.version += 1
        self.repo.insert_entity_and_event("INSERT INTO objectives(objective_id, project_id, key, direction, value, version, source_parent_objective_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (imported.objective_id, imported.project_id, imported.key, imported.direction, imported.value, imported.version, imported.source_parent_objective_id), child, self._event(child.project_id, "OBJECTIVE_IMPORTED", asdict(imported)))
        return self._ok(asdict(imported))

    def project_create(self, args: list[str]) -> dict:
        if len(args) < 2: raise SICLError("INVALID_ARGUMENT", "project_id and name required")
        if len(args) > 4: raise SICLError("INVALID_ARGUMENT", "project_id name [spatial_scope] [temporal_scope]")
        project_id, name = args[0], " ".join(args[1:2])
        spatial_scope = self._parse_spatial(args[2]) if len(args) >= 3 else None
        temporal_scope = self._parse_temporal(args[3]) if len(args) == 4 else TemporalScope.PROYECTO
        if self.repo.get_project(project_id): raise SICLError("PROJECT_ALREADY_EXISTS", project_id)
        p = Project(project_id, name, spatial_scope=spatial_scope, temporal_scope=temporal_scope)
        self.repo.insert_project(p, self._event(project_id, "PROJECT_CREATED", {"name": name, "spatial_scope": spatial_scope.value if spatial_scope else None, "temporal_scope": temporal_scope.value}))
        self.current_project = project_id
        return self._ok(asdict(p))

    @staticmethod
    def _parse_spatial(value: str) -> SpatialScope:
        try:
            return SpatialScope(value.lower())
        except ValueError as exc:
            raise SICLError("INVALID_SCOPE", f"invalid spatial_scope: {value}") from exc

    @staticmethod
    def _parse_temporal(value: str) -> TemporalScope:
        try:
            return TemporalScope(value.lower())
        except ValueError as exc:
            raise SICLError("INVALID_SCOPE", f"invalid temporal_scope: {value}") from exc

    def project_set_scope(self, args: list[str]) -> dict:
        if len(args) not in (1, 2):
            raise SICLError("INVALID_ARGUMENT", "spatial_scope [temporal_scope] required")
        p = self._require_open()
        spatial_scope = self._parse_spatial(args[0])
        temporal_scope = self._parse_temporal(args[1]) if len(args) == 2 else p.temporal_scope
        p.spatial_scope = spatial_scope
        p.temporal_scope = temporal_scope
        p.version += 1
        event = self._event(p.project_id, "SCOPE_CHANGED", {"spatial_scope": spatial_scope.value, "temporal_scope": temporal_scope.value})
        self.repo.update_project_and_event(
            p,
            event,
            "UPDATE projects SET spatial_scope=?, temporal_scope=? WHERE project_id=?",
            (spatial_scope.value, temporal_scope.value, p.project_id),
        )
        return self._ok(asdict(p))

    def project_open(self, args: list[str]) -> dict:
        if len(args) != 1: raise SICLError("INVALID_ARGUMENT", "project_id required")
        if not self.repo.get_project(args[0]): raise SICLError("PROJECT_NOT_FOUND", args[0])
        self.current_project = args[0]
        return self.project_show()

    def project_show(self) -> dict:
        return self._ok(asdict(self._project()))

    def stage_set(self, args: list[str]) -> dict:
        if len(args) != 1 or args[0].upper() not in STAGES: raise SICLError("INVALID_ARGUMENT", "stage must be DRAFT, ACTIVE or CLOSED")
        p = self._require_open(); stage = args[0].upper(); p.stage = stage; p.version += 1
        self.repo.update_project_and_event(p, self._event(p.project_id, "STAGE_SET", {"stage": stage}), "UPDATE projects SET stage=? WHERE project_id=?", (stage, p.project_id))
        return self._ok(asdict(p))

    def objective_set(self, args: list[str]) -> dict:
        if len(args) != 3 or args[1].upper() not in DIRECTIONS: raise SICLError("INVALID_ARGUMENT", "key direction value required")
        p = self._require_open(); key, direction, value = args[0], args[1].upper(), args[2]; oid = f"OBJ-{uuid.uuid4().hex[:10]}"; o = Objective(oid, p.project_id, key, direction, value); p.objectives[oid] = o; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO objectives(objective_id, project_id, key, direction, value, version, source_parent_objective_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (oid, p.project_id, key, direction, value, 1, None), p, self._event(p.project_id, "OBJECTIVE_SET", asdict(o)))
        return self._ok(asdict(o))

    def constraint_set(self, args: list[str], *, source: str = "USER_COMMAND") -> dict:
        if len(args) not in (3, 4): raise SICLError("INVALID_ARGUMENT", "key operator value [unit] required")
        p = self._require_open(); key, operator, value = args[:3]; unit = args[3] if len(args) == 4 else ""; cid = f"CON-{uuid.uuid4().hex[:10]}"; c = Constraint(cid, p.project_id, key, operator, value, unit, True); p.constraints[cid] = c; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO constraints_ VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (cid, p.project_id, key, operator, value, unit, 1, 1), p, self._event(p.project_id, "CONSTRAINT_SET", asdict(c), source))
        return self._ok(asdict(c))

    def role_add(self, args: list[str]) -> dict:
        if len(args) < 1: raise SICLError("INVALID_ARGUMENT", "name required")
        p = self._require_open(); name, actor = args[0], " ".join(args[1:]) or self.actor; rid = f"ROLE-{uuid.uuid4().hex[:10]}"; r = Role(rid, p.project_id, name, actor); p.roles[rid] = r; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO roles VALUES (?, ?, ?, ?, ?)", (rid, p.project_id, name, actor, 1), p, self._event(p.project_id, "ROLE_ADDED", asdict(r)))
        return self._ok(asdict(r))

    def actor_add(self, args: list[str]) -> dict:
        if len(args) not in {4, 6}:
            raise SICLError("INVALID_ARGUMENT", "actor_id role name authority_level [interests_json constraints_json] required")
        p = self._require_open()
        actor_id, role_text, name, authority_text = args[:4]
        if actor_id in p.actors:
            raise SICLError("CONFLICT", f"actor already exists: {actor_id}")
        try:
            role = ActorRole(role_text.upper())
            authority = AuthorityLevel(authority_text.upper())
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid actor role or authority level") from exc
        try:
            interests = json.loads(args[4]) if len(args) == 6 else []
            constraints = json.loads(args[5]) if len(args) == 6 else []
            if not isinstance(interests, list) or not isinstance(constraints, list):
                raise ValueError
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SICLError("INVALID_ARGUMENT", "interests and constraints must be JSON lists") from exc
        actor = Actor(actor_id, p.project_id, role, name, authority, interests, constraints)
        p.actors[actor_id] = actor
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO actors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (actor.actor_id, actor.project_id, actor.role.value, actor.name, actor.authority_level.value, json.dumps(actor.interests), json.dumps(actor.constraints), actor.state.value, actor.created_at.isoformat(), actor.version),
            p,
            self._event(p.project_id, "ACTOR_ADDED", actor_to_dict(actor)),
        )
        return self._ok({"actor": actor_to_dict(actor)})

    def actor_list(self) -> dict:
        return self._ok({"actors": [actor_to_dict(item) for item in self.repo.list_actors(self._project().project_id)]})

    def actor_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "actor_id required")
        actor = self.repo.get_actor(self._project().project_id, args[0])
        if actor is None:
            raise SICLError("ACTOR_NOT_FOUND", args[0])
        return self._ok({"actor": actor_to_dict(actor)})

    def position_add(self, args: list[str]) -> dict:
        if len(args) < 5:
            raise SICLError("INVALID_ARGUMENT", "actor_id subject_type subject_id stance reason required")
        p = self._require_open()
        actor_id, subject_text, subject_id, stance_text = args[:4]
        reason = args[4]
        conditions = []
        if len(args) > 5:
            try:
                conditions = json.loads(args[5])
                if not isinstance(conditions, list):
                    raise ValueError
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                raise SICLError("INVALID_ARGUMENT", "conditions must be a JSON list") from exc
        actor = p.actors.get(actor_id)
        if actor is None:
            raise SICLError("ACTOR_NOT_FOUND", actor_id)
        try:
            subject_type = SubjectType(subject_text.upper())
            stance = Stance(stance_text.upper())
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid subject type or stance") from exc
        position = ActorPosition(f"POS-{uuid.uuid4().hex[:10]}", p.project_id, actor_id, subject_type, subject_id, stance, reason, conditions)
        p.positions[position.position_id] = position
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO actor_positions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (position.position_id, position.project_id, position.actor_id, position.subject_type.value, position.subject_id, position.stance.value, position.reason, json.dumps(position.conditions), position.created_at.isoformat(), position.version),
            p,
            self._event(p.project_id, "ACTOR_POSITION_RECORDED", position_to_dict(position)),
        )
        return self._ok({"position": position_to_dict(position)})

    def position_list(self, args: list[str]) -> dict:
        if len(args) > 1:
            raise SICLError("INVALID_ARGUMENT", "optional subject_id only")
        return self._ok({"positions": [position_to_dict(item) for item in self.repo.list_positions(self._project().project_id, args[0] if args else None)]})

    def cycle_create(self, args: list[str]) -> dict:
        if len(args) not in {3, 7}:
            raise SICLError("INVALID_ARGUMENT", "cycle_id horizon start_date [end_date assumptions_json objectives_json actors_json] required")
        p = self._require_open(); cycle_id, horizon_text, start_text = args[:3]
        if cycle_id in p.temporal_cycles:
            raise SICLError("CONFLICT", f"cycle already exists: {cycle_id}")
        try:
            horizon = CycleHorizon(horizon_text.upper())
            start_date = date.fromisoformat(start_text)
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid horizon or ISO start_date") from exc
        try:
            end_date = date.fromisoformat(args[3]) if len(args) == 7 and args[3] not in {"", "NONE", "NULL"} else None
            assumptions = json.loads(args[4]) if len(args) == 7 else []
            objectives = json.loads(args[5]) if len(args) == 7 else []
            actors = json.loads(args[6]) if len(args) == 7 else []
            if not all(isinstance(item, list) for item in (assumptions, objectives, actors)):
                raise ValueError
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid cycle JSON fields") from exc
        cycle = TemporalCycle(cycle_id, p.project_id, horizon, start_date, end_date, assumptions, objectives, actors)
        p.temporal_cycles[cycle_id] = cycle; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO temporal_cycles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (cycle.cycle_id, cycle.project_id, cycle.horizon.value, cycle.start_date.isoformat(), None, json.dumps(cycle.assumptions), json.dumps(cycle.objectives_at_horizon), json.dumps(cycle.actors_involved), cycle.state.value, cycle.created_at.isoformat(), cycle.version), p, self._event(p.project_id, "TEMPORAL_CYCLE_CREATED", cycle_to_dict(cycle)))
        return self._ok({"cycle": cycle_to_dict(cycle)})

    def cycle_list(self) -> dict:
        return self._ok({"cycles": [cycle_to_dict(item) for item in self.repo.list_cycles(self._project().project_id)]})

    def cycle_show(self, args: list[str]) -> dict:
        if len(args) != 1: raise SICLError("INVALID_ARGUMENT", "cycle_id required")
        cycle = self.repo.get_cycle(self._project().project_id, args[0])
        if cycle is None: raise SICLError("CYCLE_NOT_FOUND", args[0])
        return self._ok({"cycle": cycle_to_dict(cycle)})

    def scenario_create(self, args: list[str]) -> dict:
        if len(args) not in {3, 5}: raise SICLError("INVALID_ARGUMENT", "branch_id parent_cycle_id name [conditions_json objectives_json] required")
        p = self._require_open(); branch_id, parent_text, name = args[:3]
        if branch_id in p.scenario_branches: raise SICLError("CONFLICT", f"scenario already exists: {branch_id}")
        parent_id = None if parent_text.upper() in {"NONE", "NULL", "-"} else parent_text
        if parent_id and parent_id not in p.temporal_cycles: raise SICLError("CYCLE_NOT_FOUND", parent_id)
        try:
            conditions = json.loads(args[3]) if len(args) == 5 else {}
            objectives = json.loads(args[4]) if len(args) == 5 else []
            if not isinstance(conditions, dict) or not isinstance(objectives, list): raise ValueError
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid scenario JSON fields") from exc
        branch = ScenarioBranch(branch_id, p.project_id, parent_id, name, conditions, objectives)
        p.scenario_branches[branch_id] = branch; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO scenario_branches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (branch.branch_id, branch.project_id, branch.parent_cycle_id, branch.scenario_name, json.dumps(branch.conditions), json.dumps(branch.objectives), branch.state.value, branch.selected_by, None, branch.created_at.isoformat(), branch.version), p, self._event(p.project_id, "SCENARIO_BRANCH_CREATED", scenario_to_dict(branch)))
        return self._ok({"scenario": scenario_to_dict(branch)})

    def scenario_list(self) -> dict:
        return self._ok({"scenarios": [scenario_to_dict(item) for item in self.repo.list_scenarios(self._project().project_id)]})

    def scenario_select(self, args: list[str]) -> dict:
        if len(args) != 3: raise SICLError("INVALID_ARGUMENT", "branch_id actor authority required")
        p = self._require_open(); branch_id, actor, authority = args
        branch = p.scenario_branches.get(branch_id)
        if branch is None: raise SICLError("SCENARIO_NOT_FOUND", branch_id)
        if branch.state is ScenarioState.SELECTED: raise SICLError("CONFLICT", "scenario already selected")
        if actor not in p.actors or p.actors[actor].state is not ActorState.ACTIVE: raise SICLError("ACTOR_REQUIRED", actor)
        if not any(review.actor == actor and review.authority == authority and review.status == "APPROVED" for review in p.human_reviews.values()): raise SICLError("HUMAN_REVIEW_REQUIRED", "approved HumanReview is required")
        selected = ScenarioBranch(branch.branch_id, branch.project_id, branch.parent_cycle_id, branch.scenario_name, branch.conditions, branch.objectives, ScenarioState.SELECTED, actor, datetime.now(timezone.utc), branch.created_at, branch.version + 1)
        p.scenario_branches[branch_id] = selected; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO scenario_branches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (selected.branch_id, selected.project_id, selected.parent_cycle_id, selected.scenario_name, json.dumps(selected.conditions), json.dumps(selected.objectives), selected.state.value, selected.selected_by, selected.selected_at.isoformat(), selected.created_at.isoformat(), selected.version), p, self._event(p.project_id, "SCENARIO_SELECTED", scenario_to_dict(selected)))
        return self._ok({"scenario": scenario_to_dict(selected)})

    def evolution_create(self, args: list[str]) -> dict:
        if len(args) != 4:
            raise SICLError("INVALID_ARGUMENT", "evolution_id scenario_id from_cycle_id to_cycle_id required")
        p = self._require_open(); evolution_id, scenario_id, from_cycle_id, to_cycle_id = args
        if evolution_id in p.scenario_evolutions:
            raise SICLError("CONFLICT", f"evolution already exists: {evolution_id}")
        if scenario_id not in p.scenario_branches:
            raise SICLError("SCENARIO_NOT_FOUND", scenario_id)
        if from_cycle_id not in p.temporal_cycles or to_cycle_id not in p.temporal_cycles:
            raise SICLError("CYCLE_NOT_FOUND", "from_cycle_id and to_cycle_id must exist")
        evolution = ScenarioEvolution(evolution_id, scenario_id, from_cycle_id, to_cycle_id)
        p.scenario_evolutions[evolution_id] = evolution; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO scenario_evolutions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (evolution_id, p.project_id, scenario_id, from_cycle_id, to_cycle_id, "[]", "[]", evolution.state.value, None, None, 1), p, self._event(p.project_id, "SCENARIO_EVOLUTION_CREATED", evolution_to_dict(evolution)))
        return self._ok({"evolution": evolution_to_dict(evolution)})

    def evolution_add(self, args: list[str]) -> dict:
        if len(args) < 3 or args[0].upper() not in {"CHANGE", "TRIGGER"}:
            raise SICLError("INVALID_ARGUMENT", "CHANGE evolution_id key value or TRIGGER evolution_id trigger required")
        p = self._require_open(); kind, evolution_id = args[0].upper(), args[1]
        evolution = p.scenario_evolutions.get(evolution_id)
        if evolution is None: raise SICLError("EVOLUTION_NOT_FOUND", evolution_id)
        if evolution.state is not EvolutionState.PROPOSED: raise SICLError("INVALID_STATE", "only PROPOSED evolution can be edited")
        changes = list(evolution.changes); triggers = list(evolution.triggers)
        if kind == "CHANGE":
            if len(args) < 4: raise SICLError("INVALID_ARGUMENT", "key and value required")
            changes.append({"key": args[2], "value": " ".join(args[3:])})
        else:
            triggers.append(" ".join(args[2:]))
        updated = ScenarioEvolution(evolution.evolution_id, evolution.scenario_id, evolution.from_cycle_id, evolution.to_cycle_id, changes, triggers, evolution.state, evolution.applied_by, evolution.applied_at, evolution.version + 1)
        p.scenario_evolutions[evolution_id] = updated; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO scenario_evolutions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (updated.evolution_id, p.project_id, updated.scenario_id, updated.from_cycle_id, updated.to_cycle_id, json.dumps(updated.changes), json.dumps(updated.triggers), updated.state.value, None, None, updated.version), p, self._event(p.project_id, "SCENARIO_EVOLUTION_UPDATED", evolution_to_dict(updated)))
        return self._ok({"evolution": evolution_to_dict(updated)})

    def evolution_apply(self, args: list[str]) -> dict:
        if len(args) < 3: raise SICLError("HUMAN_AUTHORITY_REQUIRED", "evolution_id actor authority required")
        p = self._require_open(); evolution_id, actor, authority = args[0], args[1], " ".join(args[2:])
        if not actor.strip() or not authority.strip(): raise SICLError("HUMAN_AUTHORITY_REQUIRED", "actor and authority required")
        evolution = p.scenario_evolutions.get(evolution_id)
        if evolution is None: raise SICLError("EVOLUTION_NOT_FOUND", evolution_id)
        if evolution.state is EvolutionState.APPLIED: raise SICLError("CONFLICT", "evolution already applied")
        applied = ScenarioEvolution(evolution.evolution_id, evolution.scenario_id, evolution.from_cycle_id, evolution.to_cycle_id, evolution.changes, evolution.triggers, EvolutionState.APPLIED, actor, datetime.now(timezone.utc), evolution.version + 1)
        p.scenario_evolutions[evolution_id] = applied; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO scenario_evolutions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (applied.evolution_id, p.project_id, applied.scenario_id, applied.from_cycle_id, applied.to_cycle_id, json.dumps(applied.changes), json.dumps(applied.triggers), applied.state.value, applied.applied_by, applied.applied_at.isoformat(), applied.version), p, self._event(p.project_id, "SCENARIO_EVOLUTION_APPLIED", {**evolution_to_dict(applied), "authority": authority}))
        return self._ok({"evolution": evolution_to_dict(applied), "decision_created": False, "recommendation_created": False})

    def evolution_list(self) -> dict:
        return self._ok({"evolutions": [evolution_to_dict(item) for item in self.repo.list_scenario_evolutions(self._project().project_id)]})

    def evolution_show(self, args: list[str]) -> dict:
        if len(args) != 1: raise SICLError("INVALID_ARGUMENT", "evolution_id required")
        evolution = self.repo.get_scenario_evolution(self._project().project_id, args[0])
        if evolution is None: raise SICLError("EVOLUTION_NOT_FOUND", args[0])
        return self._ok({"evolution": evolution_to_dict(evolution)})

    def fact_set(self, args: list[str], *, event_source: str = "USER_COMMAND") -> dict:
        if not args: raise SICLError("INVALID_ARGUMENT", "statement required")
        p = self._require_open(); statement, source = args[0], " ".join(args[1:]); fid = f"FACT-{uuid.uuid4().hex[:10]}"; f = Fact(fid, p.project_id, statement, source); p.facts[fid] = f; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO facts VALUES (?, ?, ?, ?, ?)", (fid, p.project_id, statement, source, 1), p, self._event(p.project_id, "FACT_SET", asdict(f), event_source))
        return self._ok(asdict(f))

    def site_intelligence(self, location: str) -> dict:
        if not location:
            raise SICLError("INVALID_ARGUMENT", "location required")
        try:
            observation = get_site_observation(location)
        except ValueError:
            return {"status": "REQUIRES_HUMAN_DECISION", "code": "LOCATION_NOT_RECOGNIZED", "message": "Ubicación no reconocida. Ingrese datos manualmente.", "data": {"location": location}}
        source = observation.source
        facts = [
            (f"Coordenadas: {observation.latitude}, {observation.longitude}", source),
            (f"Temperatura media observada: {observation.temperature_mean_c} °C", source),
            (f"Viento máximo medio: {observation.wind_speed_kmh} km/h; radiación: {observation.radiation_kwh_m2_day} kWh/m²/día", source),
        ]
        recorded = []
        existing = self._project()
        for statement, evidence_source in facts:
            if not any(f.statement == statement for f in existing.facts.values()):
                recorded.append(self.fact_set([statement, evidence_source], event_source=source)["data"])
                existing = self._project()
        return self._ok({"location": location, "source": source, "records": recorded, "simulated": observation.simulated, "latitude": observation.latitude, "longitude": observation.longitude})

    def assumption_set(self, args: list[str]) -> dict:
        if not args: raise SICLError("INVALID_ARGUMENT", "statement required")
        p = self._require_open(); statement, basis = args[0], " ".join(args[1:]); aid = f"ASM-{uuid.uuid4().hex[:10]}"; a = Assumption(aid, p.project_id, statement, basis); p.assumptions[aid] = a; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO assumptions VALUES (?, ?, ?, ?, ?)", (aid, p.project_id, statement, basis, 1), p, self._event(p.project_id, "ASSUMPTION_SET", asdict(a)))
        return self._ok(asdict(a))

    def evidence_add(self, args: list[str]) -> dict:
        if len(args) < 3 or len(args) > 5:
            raise SICLError("INVALID_ARGUMENT", "evidence_id statement evidence_type [source_id] [evidence_url] required")
        p = self._require_open()
        evidence_id, statement, evidence_type_text = args[:3]
        try:
            evidence_type = EvidenceType(evidence_type_text.upper())
        except ValueError as exc:
            raise SICLError("INVALID_EVIDENCE_TYPE", evidence_type_text) from exc
        if evidence_id in p.evidence:
            raise SICLError("EVIDENCE_ALREADY_EXISTS", evidence_id)
        source_id = args[3] if len(args) >= 4 else None
        evidence_url = args[4] if len(args) == 5 else None
        evidence = Evidence(
            evidence_id=evidence_id,
            project_id=p.project_id,
            source_id=source_id,
            statement=statement,
            evidence_type=evidence_type,
            captured_at=datetime.now(timezone.utc),
            method_version="CLI/1.0",
            evidence_url=evidence_url,
            evidence_hash=hashlib.sha256(statement.encode("utf-8")).hexdigest(),
            state="OBSERVED",
        )
        p.evidence[evidence_id] = evidence
        p.version += 1
        event_payload = {
            "evidence_id": evidence.evidence_id,
            "statement": evidence.statement,
            "evidence_type": evidence.evidence_type.value,
            "source_id": evidence.source_id,
            "evidence_url": evidence.evidence_url,
            "evidence_hash": evidence.evidence_hash,
            "state": evidence.state,
        }
        self.repo.insert_evidence_and_event(evidence, p, self._event(p.project_id, "EVIDENCE_ADDED", event_payload))
        return self._ok(asdict(evidence))

    def evidence_list(self) -> dict:
        return self._ok({"evidence": [asdict(item) for item in self.repo.list_evidence(self._project().project_id)]})

    def evidence_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "evidence_id required")
        evidence = self.repo.get_evidence(self._project().project_id, args[0])
        if evidence is None:
            raise SICLError("EVIDENCE_NOT_FOUND", args[0])
        return self._ok(asdict(evidence))

    def decision_record(self, args: list[str]) -> dict:
        if len(args) < 3: raise SICLError("INVALID_ARGUMENT", "statement actor authority required")
        p = self._require_open(); statement, actor, authority = args[0], args[1], " ".join(args[2:])
        registered_actor = p.actors.get(actor)
        if p.actors and (registered_actor is None or registered_actor.state is not ActorState.ACTIVE):
            raise SICLError("DECISIONAL_ACTOR_REQUIRED", "an active registered actor is required")
        if registered_actor and registered_actor.authority_level is not AuthorityLevel.DECISIONAL:
            raise SICLError("DECISIONAL_ACTOR_REQUIRED", "only DECISIONAL actors may register a Decision")
        if any(v.actor_id != actor and p.actors.get(v.actor_id, registered_actor).authority_level is AuthorityLevel.VETO and p.actors.get(v.actor_id).state is ActorState.ACTIVE and v.stance in {Stance.OPPOSE, Stance.CONDITIONAL} and v.subject_type is SubjectType.DECISION_PROPOSED for v in p.positions.values()):
            raise SICLError("VETO_BLOCKED", "an active VETO actor blocks this Decision")
        if not any(review.status == "APPROVED" and review.actor == actor and review.authority == authority for review in p.human_reviews.values()):
            raise SICLError("HUMAN_REVIEW_REQUIRED", "an approved HumanReview by the same actor and authority is required")
        did = f"DEC-{uuid.uuid4().hex[:10]}"; d = Decision(did, p.project_id, statement, actor, authority); p.decisions[did] = d; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?)", (did, p.project_id, statement, actor, authority, 1), p, self._event(p.project_id, "DECISION_RECORDED", asdict(d)))
        return self._ok(asdict(d))

    def human_review(self, args: list[str]) -> dict:
        if len(args) < 4:
            raise SICLError("INVALID_ARGUMENT", "actor timestamp review reason [authority] required")
        p = self._require_open(); actor, timestamp, review_text, reason = args[:4]; authority = args[4] if len(args) > 4 else ""
        if not timestamp.endswith("Z") and "+00:00" not in timestamp:
            raise SICLError("INVALID_ARGUMENT", "timestamp must be UTC")
        status = "APPROVED"
        if status not in {"APPROVED", "REJECTED", "PENDING"}:
            raise SICLError("INVALID_ARGUMENT", "status must be APPROVED, REJECTED or PENDING")
        review = HumanReview(f"REV-{uuid.uuid4().hex[:10]}", p.project_id, actor, timestamp, review_text, reason, authority, status)
        p.human_reviews[review.review_id] = review; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO human_reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (review.review_id, p.project_id, actor, timestamp, review_text, reason, authority, status, review.version), p, self._event(p.project_id, "HUMAN_REVIEW_RECORDED", asdict(review)))
        return self._ok(asdict(review))

    def alternative_create(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "alternative name required")
        p = self._require_open()
        aid = f"ALT-{uuid.uuid4().hex[:10]}"
        alternative = Alternative(aid, p.project_id, args[0])
        p.alternatives[aid] = alternative
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO alternatives VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (aid, p.project_id, alternative.name, alternative.description, "{}", alternative.status, alternative.version, alternative.source),
            p,
            self._event(p.project_id, "ALTERNATIVE_CREATED", asdict(alternative)),
        )
        return self._ok(asdict(alternative))

    def _alternative_by_name(self, project: Project, name: str) -> Alternative:
        for alternative in project.alternatives.values():
            if alternative.name == name.upper():
                return alternative
        raise SICLError("INVALID_ARGUMENT", f"alternative not found: {name}")

    def alternative_set(self, args: list[str]) -> dict:
        if len(args) != 3:
            raise SICLError("INVALID_ARGUMENT", "alternative parameter value required")
        p = self._require_open()
        alternative = self._alternative_by_name(p, args[0])
        alternative.parameters[args[1]] = args[2]
        p.version += 1
        self.repo.update_project_and_event(
            p,
            self._event(p.project_id, "ALTERNATIVE_PARAMETER_SET", {"alternative_id": alternative.alternative_id, "parameter": args[1], "value": args[2]}),
            "UPDATE alternatives SET parameters_json=?, version=? WHERE id=?",
            (json.dumps(alternative.parameters, sort_keys=True), alternative.version, alternative.alternative_id),
        )
        return self._ok(asdict(alternative))

    def alternative_list(self) -> dict:
        p = self._project()
        return self._ok({"alternatives": [asdict(a) for a in p.alternatives.values()]})

    def generate_design(self, args: list[str]) -> dict:
        if len(args) < 1:
            raise SICLError("INVALID_ARGUMENT", "method and JSON inputs required")
        p = self._require_open()
        method = args[0].lower()
        try:
            inputs = json.loads(" ".join(args[1:])) if len(args) > 1 else {}
        except json.JSONDecodeError as exc:
            raise SICLError("INVALID_ARGUMENT", "inputs must be valid JSON") from exc
        if not isinstance(inputs, dict):
            raise SICLError("INVALID_ARGUMENT", "inputs must be a JSON object")
        if method not in {"parametric_grid_v1", "pattern_variation_v1", "evolutionary_v1", "llm_assisted_v1"}:
            raise SICLError("METHOD_NOT_FOUND", method)
        try:
            generation = generate_candidates(p.project_id, method, inputs, f"GEN-{uuid.uuid4().hex[:10]}", project=p)
        except ValueError as exc:
            raise SICLError(str(exc), method) from exc
        p.generated_alternatives[generation.generation_id] = generation
        p.version += 1
        self.repo.insert_generation_and_event(generation, p, self._event(p.project_id, "DESIGN_GENERATION_RECORDED", generation_to_dict(generation), "SYSTEM_CALCULATION"))
        return self._ok({"generation": generation_to_dict(generation), "decision_created": False, "recommendation_created": False})

    def generate_list(self) -> dict:
        return self._ok({"generations": [generation_to_dict(item) for item in self.repo.list_generations(self._project().project_id)]})

    def generate_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "generation_id required")
        item = self.repo.get_generation(self._project().project_id, args[0])
        if item is None:
            raise SICLError("GENERATION_NOT_FOUND", args[0])
        return self._ok({"generation": generation_to_dict(item)})

    def alternative_promote(self, args: list[str]) -> dict:
        if len(args) < 4:
            raise SICLError("INVALID_ARGUMENT", "generation_id candidate_index actor authority required")
        p = self._require_open()
        generation = self.repo.get_generation(p.project_id, args[0])
        if generation is None:
            raise SICLError("GENERATION_NOT_FOUND", args[0])
        if generation.state is not GenerationState.GENERATED:
            raise SICLError("INVALID_STATE", "only GENERATED results can be promoted")
        try:
            index = int(args[1])
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "candidate_index must be an integer") from exc
        actor, authority = args[2], " ".join(args[3:])
        if not actor.strip() or not authority.strip():
            raise SICLError("HUMAN_AUTHORITY_REQUIRED", "actor and authority are required")
        if index < 0 or index >= len(generation.candidates):
            raise SICLError("CANDIDATE_NOT_FOUND", str(index))
        candidate = generation.candidates[index]
        alternative_id = f"ALT-{uuid.uuid4().hex[:10]}"
        name = str(candidate.get("name") or f"GENERATED_{generation.generation_id}_{index}")
        description = str(candidate.get("description") or generation.rationale)
        parameters = {key: value for key, value in candidate.items() if key not in {"name", "description"}}
        alternative = Alternative(alternative_id, p.project_id, name, description, parameters, "PROPOSED", 1, "DESIGN_GENERATION")
        p.alternatives[alternative_id] = alternative
        p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO alternatives VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (alternative_id, p.project_id, alternative.name, alternative.description, json.dumps(alternative.parameters, sort_keys=True), alternative.status, alternative.version, alternative.source), p, self._event(p.project_id, "GENERATED_ALTERNATIVE_PROMOTED", {"generation_id": generation.generation_id, "candidate_index": index, "alternative": asdict(alternative), "actor": actor, "authority": authority}))
        return self._ok({"alternative": asdict(alternative), "generation_id": generation.generation_id, "candidate_index": index, "decision_created": False, "recommendation_created": False})

    def memory_list(self) -> dict:
        return self._ok({"memories": [memory_to_dict(item) for item in self.repo.list_memory()]})

    def memory_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "memory_id required")
        memory = self.repo.get_memory(args[0])
        if memory is None:
            raise SICLError("MEMORY_NOT_FOUND", args[0])
        return self._ok({"memory": memory_to_dict(memory)})

    def memory_extract(self, args: list[str]) -> dict:
        if len(args) < 3:
            raise SICLError("HUMAN_AUTHORITY_REQUIRED", "project_id actor authority required")
        project_id, actor, authority = args[0], args[1], " ".join(args[2:])
        if not actor.strip() or not authority.strip():
            raise SICLError("HUMAN_AUTHORITY_REQUIRED", "actor and authority are required")
        project = self.repo.get_project(project_id)
        if project is None:
            raise SICLError("PROJECT_NOT_FOUND", project_id)
        memory = extract_memory(project)
        self.repo.insert_memory_and_event(memory, self._event(project_id, "INSTITUTIONAL_MEMORY_EXTRACTED", {"memory_id": memory.memory_id, "actor": actor, "authority": authority}))
        return self._ok({"memory": memory_to_dict(memory), "decision_created": False})

    def memory_revoke(self, args: list[str]) -> dict:
        if len(args) < 3:
            raise SICLError("HUMAN_AUTHORITY_REQUIRED", "memory_id actor authority required")
        memory_id, actor, authority = args[0], args[1], " ".join(args[2:])
        if not actor.strip() or not authority.strip():
            raise SICLError("HUMAN_AUTHORITY_REQUIRED", "actor and authority are required")
        memory = self.repo.get_memory(memory_id)
        if memory is None:
            raise SICLError("MEMORY_NOT_FOUND", memory_id)
        if memory.state is MemoryState.REVOKED:
            return self._ok({"memory": memory_to_dict(memory), "already_revoked": True})
        event_project = memory.project_id_source or "INSTITUTIONAL_MEMORY"
        revoked = self.repo.revoke_memory_and_event(memory, self._event(event_project, "INSTITUTIONAL_MEMORY_REVOKED", {"memory_id": memory_id, "actor": actor, "authority": authority}))
        return self._ok({"memory": memory_to_dict(revoked)})

    def memory_apply(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "memory_id and project_id required")
        memory_id, project_id = args
        memory = self.repo.get_memory(memory_id)
        if memory is None:
            raise SICLError("MEMORY_NOT_FOUND", memory_id)
        if memory.state is MemoryState.REVOKED:
            raise SICLError("MEMORY_REVOKED", memory_id)
        project = self.repo.get_project(project_id)
        if project is None:
            raise SICLError("PROJECT_NOT_FOUND", project_id)
        if project.stage == "CLOSED":
            raise SICLError("INVALID_STATE", "closed project cannot apply memory")
        project.version += 1
        self.repo.update_project_and_event(project, self._event(project_id, "INSTITUTIONAL_MEMORY_APPLIED", {"memory_id": memory_id, "actor": self.actor}), "UPDATE projects SET version=? WHERE project_id=?", (project.version, project_id))
        return self._ok({"memory_id": memory_id, "project_id": project_id, "applied": True, "canonical_state_changed": False})

    def agent_run(self, args: list[str]) -> dict:
        if len(args) != 2 or args[0].upper() not in {"BIOCLIMATIC", "STRUCTURAL", "ECONOMIC"}:
            raise SICLError("INVALID_ARGUMENT", "usage: /AGENT RUN BIOCLIMATIC|STRUCTURAL|ECONOMIC alternative")
        p = self._require_open()
        alternative = next((item for item in p.alternatives.values() if item.alternative_id == args[1] or item.name == args[1].upper()), None)
        if alternative is None:
            raise SICLError("INVALID_ARGUMENT", f"alternative not found: {args[1]}")
        agent_name = args[0].upper()
        agent = {"BIOCLIMATIC": BioclimaticAgent, "STRUCTURAL": StructuralAgent, "ECONOMIC": EconomicAgent}[agent_name]()
        evaluation = agent.evaluate(alternative, p)
        p.evaluations[evaluation.evaluation_id] = evaluation
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (evaluation.evaluation_id, evaluation.alternative_id, evaluation.objective_id, evaluation.value, evaluation.unit, evaluation.confidence, evaluation.source, evaluation.version),
            p,
            self._event(p.project_id, "AGENT_EVALUATION_RECORDED", asdict(evaluation), "EXPERT_SYSTEM"),
        )
        return self._ok({"agent": agent_name, "evaluation": asdict(evaluation), "decision_created": False})

    def pareto(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "two objective keys required")
        p = self._project()
        objectives = [item for key in args for item in p.objectives.values() if item.key == key]
        if len(objectives) != 2:
            raise SICLError("INVALID_STATE", "both objectives with evaluations are required")
        result = pareto_front(p.alternatives.values(), p.evaluations.values(), objectives)
        return self._ok({"non_dominated": result.non_dominated, "dominated": result.dominated, "incomplete": result.incomplete, "decision_created": False})

    def _multiobjective_result(self, method: str, objective_keys: list[str]) -> dict:
        if len(objective_keys) < 2:
            raise SICLError("INVALID_ARGUMENT", "at least two objective keys required")
        p = self._project()
        objectives = []
        for key in objective_keys:
            objective = next((item for item in p.objectives.values() if item.key == key), None)
            if objective is None:
                raise SICLError("OBJECTIVE_NOT_FOUND", key)
            if objective.direction not in DIRECTIONS:
                raise SICLError("OBJECTIVE_DIRECTION_REQUIRED", key)
            objectives.append(objective)
        alternatives = list(p.alternatives.values())
        evaluations = list(p.evaluations.values())
        result = pareto_front(alternatives, evaluations, objectives)
        values = {(item.alternative_id, item.objective_id): item.value for item in evaluations}
        matrix = {
            alternative.alternative_id: {
                objective.key: values.get((alternative.alternative_id, objective.objective_id))
                for objective in objectives
            }
            for alternative in alternatives
        }
        inputs = {
            "method": method,
            "objectives": objective_keys,
            "alternatives": [item.alternative_id for item in alternatives],
            "evaluations": [asdict(item) for item in evaluations],
        }
        inputs_hash = hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        result_id = f"MOBJ-{uuid.uuid4().hex[:10]}"
        record = MultiobjectiveResult(
            result_id,
            p.project_id,
            method,
            "1.0",
            objective_keys,
            [item.alternative_id for item in alternatives],
            result.non_dominated if method == "pareto_front_v1" else [],
            list(result.dominated),
            result.incomplete,
            {"matrix": matrix},
            MultiobjectiveState.EXECUTED if not result.incomplete else MultiobjectiveState.INSUFFICIENT,
            inputs_hash,
            datetime.now(timezone.utc),
            1,
        )
        p.multiobjective_results[record.multiobjective_id] = record
        p.version += 1
        data = asdict(record)
        data["state"] = record.state.value
        data["created_at"] = record.created_at.isoformat()
        self.repo.insert_multiobjective_and_event(record, p, self._event(p.project_id, "MULTIOBJECTIVE_RESULT_RECORDED", data, "SYSTEM_CALCULATION"))
        return self._ok({"multiobjective": data, "decision_created": False, "recommendation_created": False})

    def multiobjective_pareto(self, args: list[str]) -> dict:
        return self._multiobjective_result("pareto_front_v1", args)

    def multiobjective_tradeoffs(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "exactly two objective keys required")
        return self._multiobjective_result("tradeoff_matrix_v1", args)

    def multiobjective_list(self) -> dict:
        values = []
        for item in self._project().multiobjective_results.values():
            value = asdict(item)
            value["state"] = item.state.value
            values.append(value)
        return self._ok({"multiobjectives": values})

    def multiobjective_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "multiobjective_id required")
        item = self._project().multiobjective_results.get(args[0])
        if item is None:
            raise SICLError("MULTIOBJECTIVE_NOT_FOUND", args[0])
        value = asdict(item)
        value["state"] = item.state.value
        return self._ok({"multiobjective": value})

    def generate(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "alternative and target objectives required")
        p = self._require_open()
        alternative = next((item for item in p.alternatives.values() if item.alternative_id == args[0] or item.name == args[0].upper()), None)
        if alternative is None:
            raise SICLError("INVALID_ARGUMENT", f"alternative not found: {args[0]}")
        target_objectives = {item.upper() for item in args[1].split(",")}
        evaluations = [item for item in p.evaluations.values() if item.alternative_id == alternative.alternative_id]
        proposals = GenerativeOptimizer().generate(alternative, evaluations)
        proposals = [item for item in proposals if not target_objectives or any(item_key in target_objectives for item_key in ("ENERGY_SAVINGS", "CONSTRUCTION_COST", "ESTIMATED_COST"))]
        for proposal in proposals:
            p.alternatives[proposal.alternative_id] = proposal
            p.version += 1
            self.repo.insert_entity_and_event(
                "INSERT INTO alternatives VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (proposal.alternative_id, proposal.project_id, proposal.name, proposal.description, json.dumps(proposal.parameters, sort_keys=True), proposal.status, proposal.version, proposal.source),
                p,
                self._event(p.project_id, "ALTERNATIVE_GENERATED", asdict(proposal), proposal.source),
            )
        return self._ok({"generated": [asdict(item) for item in proposals], "decision_created": False, "recommendation_created": False})

    def tradeoff_matrix_command(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "two objective keys required")
        p = self._project()
        objectives = [item for key in args for item in p.objectives.values() if item.key == key]
        if len(objectives) != 2:
            raise SICLError("INVALID_STATE", "both objectives with evaluations are required")
        return self._text_response(tradeoff_matrix(p.alternatives.values(), p.evaluations.values(), objectives))

    def debate(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "alternative id or name required")
        p = self._project()
        alternative = next((item for item in p.alternatives.values() if item.alternative_id == args[0] or item.name == args[0].upper()), None)
        if alternative is None:
            raise SICLError("INVALID_ARGUMENT", f"alternative not found: {args[0]}")
        agents = [BioclimaticAgent(), StructuralAgent(), EconomicAgent()]
        lines = ["SICL MULTI-AGENT DEBATE", f"Alternative: {alternative.name}", ""]
        evaluations = []
        for agent in agents:
            try:
                evaluation = agent.evaluate(alternative, p)
                evaluations.append(evaluation)
                stance = "aprueba" if evaluation.value >= 0 else "rechaza"
                lines.append(f"El Agente {agent.name.title()} {stance}: {evaluation.value} {evaluation.unit} (EXPERT_SYSTEM).")
            except ValueError as error:
                lines.append(f"El Agente {agent.name.title()} requiere datos: {error}.")
        if evaluations:
            positive = sum(item.value >= 0 for item in evaluations)
            verdict = f"{positive}/{len(evaluations)} agentes producen evaluaciones no negativas; revisar trade-offs antes de decidir."
        else:
            verdict = "No hay evaluaciones suficientes para un veredicto analítico."
        lines.extend(["", f"VEREDICTO DEL DEBATE: {verdict}", "DECISION CREADA: NO"])
        return self._text_response("\n".join(lines) + "\n")

    def evaluate(self, args: list[str]) -> dict:
        if len(args) < 3 or len(args) > 6:
            raise SICLError("INVALID_ARGUMENT", "alternative objective value [unit] [confidence] [source] required")
        p = self._require_open()
        alternative = self._alternative_by_name(p, args[0])
        objective = next((o for o in p.objectives.values() if o.key == args[1]), None)
        if objective is None:
            raise SICLError("INVALID_STATE", "an Objective is required before Evaluation")
        unit = args[3] if len(args) >= 4 else ""
        confidence = float(args[4]) if len(args) >= 5 and args[4] else 1.0
        source = args[5] if len(args) >= 6 else "USER_INPUT"
        if source not in EVALUATION_SOURCES:
            raise SICLError("INVALID_ARGUMENT", "invalid evaluation source")
        evaluation = Evaluation(f"EVAL-{uuid.uuid4().hex[:10]}", alternative.alternative_id, objective.objective_id, float(args[2]), unit, confidence, source)
        p.evaluations[evaluation.evaluation_id] = evaluation
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (evaluation.evaluation_id, evaluation.alternative_id, evaluation.objective_id, evaluation.value, evaluation.unit, evaluation.confidence, evaluation.source, evaluation.version),
            p,
            self._event(p.project_id, "EVALUATION_RECORDED", asdict(evaluation)),
        )
        return self._ok(asdict(evaluation))

    def compare(self, args: list[str]) -> dict:
        if len(args) < 2:
            raise SICLError("INVALID_ARGUMENT", "at least two alternatives required")
        p = self._require_open()
        alternatives = [self._alternative_by_name(p, name) for name in args]
        evaluations = [e for e in p.evaluations.values() if e.alternative_id in {a.alternative_id for a in alternatives}]
        comparison = Comparison(f"CMP-{uuid.uuid4().hex[:10]}", p.project_id, [a.alternative_id for a in alternatives], evaluations)
        p.comparisons[comparison.comparison_id] = comparison
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO comparisons VALUES (?, ?, ?, ?, ?, ?)",
            (comparison.comparison_id, p.project_id, json.dumps(comparison.alternative_ids), json.dumps([e.evaluation_id for e in evaluations]), json.dumps(comparison.tradeoffs), comparison.version),
            p,
            self._event(p.project_id, "COMPARISON_CREATED", {"comparison_id": comparison.comparison_id, "alternative_ids": comparison.alternative_ids}),
        )
        return self._ok(asdict(comparison))

    def simulate_run(self, args: list[str]) -> dict:
        if len(args) < 2:
            raise SICLError("INVALID_ARGUMENT", "simulation_type method [params] required")
        try:
            simulation_type = SimulationType(args[0].upper())
        except ValueError as exc:
            raise SICLError("INVALID_ARGUMENT", "invalid simulation type") from exc
        p = self._require_open()
        inputs: dict[str, Any] = {}
        raw = " ".join(args[2:]).strip()
        if raw:
            try:
                inputs = json.loads(raw)
            except json.JSONDecodeError:
                for item in args[2:]:
                    if "=" not in item:
                        raise SICLError("INVALID_ARGUMENT", "simulation params must be JSON or key=value")
                    key, value = item.split("=", 1)
                    try:
                        inputs[key] = json.loads(value)
                    except json.JSONDecodeError:
                        inputs[key] = value
        started = now_utc()
        method = args[1]
        try:
            state, outputs = execute_method(simulation_type, method, inputs, p)
        except KeyError as exc:
            raise SICLError("METHOD_NOT_FOUND", method) from exc
        except ValueError as exc:
            if str(exc) == "METHOD_TYPE_MISMATCH":
                raise SICLError("METHOD_TYPE_MISMATCH", method)
            if str(exc) == "PARAMETER_NOT_FOUND":
                raise SICLError("PARAMETER_NOT_FOUND", str(inputs.get("parameter_name", "")))
            if str(exc) == "INVALID_DISTRIBUTION":
                raise SICLError("INVALID_DISTRIBUTION", "supported distributions: NORMAL, UNIFORM, TRIANGULAR")
            if str(exc) == "INVALID_INPUTS":
                raise SICLError("INVALID_INPUTS", "iterations must be between 1 and 10000 and parameters must be numeric")
            state, outputs = SimulationState.FAILED, {"error": str(exc)}
        finished = now_utc()
        simulation = Simulation(f"SIM-{uuid.uuid4().hex[:10]}", p.project_id, simulation_type, method, METHODS.get(method, {}).get("method_version", "unknown"), inputs, outputs, state, started, finished, canonical_hash(inputs, outputs, outputs.get("seed")))
        p.simulations[simulation.simulation_id] = simulation
        p.version += 1
        self.repo.insert_simulation_and_event(simulation, p, self._event(p.project_id, "SIMULATION_RECORDED", simulation_to_dict(simulation), "SIMULATION"))
        return self._ok({"simulation": simulation_to_dict(simulation), "decision_created": False, "recommendation_created": False})

    def simulate_monte_carlo(self, args: list[str]) -> dict:
        if len(args) not in {4, 5}:
            raise SICLError("INVALID_ARGUMENT", "alternative_id objective_id parameter_name distribution_json [iterations] required")
        try:
            distribution = json.loads(args[3])
            if not isinstance(distribution, dict):
                raise ValueError
            iterations = int(args[4]) if len(args) == 5 else 1000
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SICLError("INVALID_INPUTS", "distribution must be JSON and iterations numeric") from exc
        inputs = {
            "alternative_id": args[0],
            "objective_id": args[1],
            "parameter_name": args[2],
            "parameter_distribution": distribution,
            "iterations": iterations,
            "seed": 20260916,
        }
        return self.simulate_run(["MONTE_CARLO", "monte_carlo_v1", json.dumps(inputs, sort_keys=True)])

    def simulate_list(self) -> dict:
        return self._ok({"simulations": [simulation_to_dict(item) for item in self.repo.list_simulations(self._project().project_id)]})

    def simulate_show(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "simulation_id required")
        simulation = self.repo.get_simulation(self._project().project_id, args[0])
        if simulation is None:
            raise SICLError("SIMULATION_NOT_FOUND", args[0])
        return self._ok({"simulation": simulation_to_dict(simulation)})

    def recommend(self) -> dict:
        p = self._require_open()
        if not p.comparisons:
            raise SICLError("INVALID_STATE", "Comparison required before Recommendation")
        comparison = next(reversed(p.comparisons.values()))
        scores: dict[str, list[float]] = {aid: [] for aid in comparison.alternative_ids}
        for evaluation in comparison.evaluations:
            scores.setdefault(evaluation.alternative_id, []).append(evaluation.value * evaluation.confidence)
        recommended_id = max(scores, key=lambda aid: sum(scores[aid]) / len(scores[aid]) if scores[aid] else float("-inf"))
        recommendation = Recommendation(f"REC-{uuid.uuid4().hex[:10]}", comparison.comparison_id, recommended_id, "Highest deterministic weighted evaluation score", 0.5)
        p.recommendations[recommendation.recommendation_id] = recommendation
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO recommendations VALUES (?, ?, ?, ?, ?, ?, ?)",
            (recommendation.recommendation_id, recommendation.comparison_id, recommendation.recommended_alternative_id, recommendation.reason, recommendation.confidence, recommendation.status, recommendation.version),
            p,
            self._event(p.project_id, "RECOMMENDATION_CREATED", asdict(recommendation)),
        )
        return self._ok(asdict(recommendation))

    def export_project(self, args: list[str]) -> dict:
        project = self._project()
        target = args[0] if args else f"exports/{project.project_id}.json"
        path = export_project_json(self.repo, project, target)
        return self._ok({"path": str(path)})

    def export_csv_command(self, args: list[str]) -> dict:
        project = self._project()
        directory = args[0] if args else "exports"
        paths = export_csv(self.repo, project, directory)
        return self._ok({"paths": [str(path) for path in paths]})

    def export_report_command(self, args: list[str]) -> dict:
        project = self._project()
        target = args[0] if args else f"exports/{project.project_id}_report.txt"
        path = export_report(self.repo, project, target)
        return self._ok({"path": str(path)})

    def import_csv_command(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "csv path and entity type required")
        path, entity_type = args[0], args[1].upper()
        if entity_type not in {"OBJECTIVES", "CONSTRAINTS"}:
            raise SICLError("INVALID_ARGUMENT", "supported imports: OBJECTIVES, CONSTRAINTS")
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        required = {"OBJECTIVES": {"key", "direction", "value"}, "CONSTRAINTS": {"key", "operator", "value"}}[entity_type]
        if rows and not required.issubset(rows[0]):
            raise SICLError("INVALID_ARGUMENT", f"CSV missing columns: {sorted(required - set(rows[0]))}")
        for row in rows:
            if entity_type == "OBJECTIVES":
                result = self.objective_set([row["key"], row["direction"], row["value"]])
            else:
                args = [row["key"], row["operator"], row["value"]]
                if row.get("unit"):
                    args.append(row["unit"])
                result = self.constraint_set(args)
            if result["code"] != "OK":
                raise SICLError("IMPORT_FAILED", result["message"])
        return self._ok({"imported": len(rows), "entity_type": entity_type})


    def variable_add(self, args: list[str]) -> dict:
        if len(args) < 6:
            raise SICLError("INVALID_ARGUMENT", "variable_id key type value actor authority [unit] [scope]")
        project = self._require_open()
        variable_id, key, kind, raw_value, actor_id, authority = args[:6]
        unit = args[6] if len(args) > 6 else None
        scope = args[7] if len(args) > 7 else (project.spatial_scope.value if project.spatial_scope else "edificacion")
        try:
            variable_type = VariableType(kind.upper())
            value: Any = json.loads(raw_value)
        except (ValueError, json.JSONDecodeError) as exc:
            if isinstance(exc, json.JSONDecodeError):
                value = raw_value
            else:
                raise SICLError("INVALID_ARGUMENT", "type must be OBJECTIVE, CONSTRAINT or PARAMETER") from exc
        variable = ProjectVariable(variable_id, project.project_id, normalized_key(key), variable_type, value, actor_id, authority, unit, scope)
        existing = [ProjectVariable(**v) if isinstance(v, dict) else v for v in project.project_variables.values()]
        try:
            validate_project_variable_uniqueness(existing, variable)
        except ValueError as exc:
            raise SICLError("CONFLICT", str(exc)) from exc
        project.project_variables[variable.variable_id] = project_variable_dict(variable)
        project.version += 1
        self.repo.add_event(self._event(project.project_id, "PROJECT_VARIABLE_RECORDED", project_variable_dict(variable)))
        return self._ok({"variable": project_variable_dict(variable), "decision_created": False})

    def variable_list(self) -> dict:
        project = self._project()
        return self._ok({"variables": list(project.project_variables.values())})

    def feasibility_check(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "alternative_id values_json required")
        project = self._project()
        try:
            values = json.loads(args[1])
        except json.JSONDecodeError as exc:
            raise SICLError("INVALID_ARGUMENT", "values_json must be valid JSON") from exc
        constraints = [asdict(item) for item in project.constraints.values()]
        result = evaluate_feasibility(args[0], values, constraints, evaluated_by=self.actor)
        project.feasibility_results[result.alternative_id] = serialize_result(result)
        self.repo.add_event(self._event(project.project_id, "FEASIBILITY_EVALUATED", serialize_result(result)))
        return self._ok({"feasibility": serialize_result(result), "decision_created": False, "recommendation_created": False})

    def multiobjective_feasible_pareto(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "pareto_ids_json required")
        project = self._project()
        try:
            front = json.loads(args[0])
        except json.JSONDecodeError as exc:
            raise SICLError("INVALID_ARGUMENT", "pareto_ids_json must be valid JSON") from exc
        results = []
        for payload in project.feasibility_results.values():
            from .feasibility import FeasibilityState, FeasibilityResult, ConstraintCheck
            checks = tuple(ConstraintCheck(**item) for item in payload.get("checks", []))
            results.append(FeasibilityResult(payload["alternative_id"], FeasibilityState(payload["state"]), checks, tuple(payload.get("failed_constraint_ids", [])), tuple(payload.get("unknown_constraint_ids", [])), tuple(payload.get("insufficient_constraint_ids", [])), tuple(), tuple(), payload.get("evaluated_by", self.actor)))
        return self._ok({"pareto_front": front, "feasible_pareto_front": feasible_pareto_front(front, results)})
