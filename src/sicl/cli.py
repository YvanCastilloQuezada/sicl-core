from __future__ import annotations

import shlex
import uuid
import json
import csv
from dataclasses import asdict

from .domain import Assumption, Constraint, Decision, Event, Fact, Objective, Project, Role, DIRECTIONS, STAGES, now_iso
from .repository import SICLError, SQLiteRepository
from .v11 import Alternative, Comparison, Evaluation, Recommendation, EVALUATION_SOURCES
from .export import dashboard_text, export_csv, export_project_json, export_report, report_text, tradeoffs_text
from .site_intelligence import get_site_observation
from .agents import BioclimaticAgent, EconomicAgent, StructuralAgent
from .optimization import pareto_front


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
                return self._ok({"commands": ["/PROJECT CREATE", "/PROJECT OPEN", "/PROJECT SHOW", "/PROJECT LIST", "/STAGE SET", "/OBJECTIVE SET", "/CONSTRAINT SET", "/ROLE ADD", "/FACT SET", "/ASSUMPTION SET", "/SITE INTELLIGENCE", "/DECISION RECORD", "/STATUS", "/HISTORY", "/EXIT"]})
            head = tuple(p.upper() for p in parts[:2])
            if head == ("/EXIT",):
                self.closed = True
                return self._ok({"closed": True})
            if head == ("/PROJECT", "CREATE"):
                return self.project_create(parts[2:])
            if head == ("/PROJECT", "OPEN"):
                return self.project_open(parts[2:])
            if head == ("/PROJECT", "SHOW"):
                return self.project_show()
            if head == ("/PROJECT", "LIST"):
                return self._ok({"projects": [asdict(p) for p in self.repo.list_projects()]})
            if head == ("/STAGE", "SET"):
                return self.stage_set(parts[2:])
            if head == ("/OBJECTIVE", "SET"):
                return self.objective_set(parts[2:])
            if head == ("/CONSTRAINT", "SET"):
                return self.constraint_set(parts[2:])
            if head == ("/ROLE", "ADD"):
                return self.role_add(parts[2:])
            if head == ("/FACT", "SET"):
                return self.fact_set(parts[2:])
            if head == ("/ASSUMPTION", "SET"):
                return self.assumption_set(parts[2:])
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

    def project_create(self, args: list[str]) -> dict:
        if len(args) < 2: raise SICLError("INVALID_ARGUMENT", "project_id and name required")
        project_id, name = args[0], " ".join(args[1:])
        if self.repo.get_project(project_id): raise SICLError("PROJECT_ALREADY_EXISTS", project_id)
        p = Project(project_id, name)
        self.repo.insert_project(p, self._event(project_id, "PROJECT_CREATED", {"name": name}))
        self.current_project = project_id
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
        self.repo.insert_entity_and_event("INSERT INTO objectives VALUES (?, ?, ?, ?, ?, ?)", (oid, p.project_id, key, direction, value, 1), p, self._event(p.project_id, "OBJECTIVE_SET", asdict(o)))
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
        if not any(c.key == "ZONIFICACION" and c.value == "C-2 (Comercial)" for c in existing.constraints.values()):
            recorded.append(self.constraint_set(["ZONIFICACION", "=", "C-2 (Comercial)", "Municipalidad"], source=source)["data"])
        return self._ok({"location": location, "source": source, "records": recorded, "simulated": observation.simulated, "latitude": observation.latitude, "longitude": observation.longitude})

    def assumption_set(self, args: list[str]) -> dict:
        if not args: raise SICLError("INVALID_ARGUMENT", "statement required")
        p = self._require_open(); statement, basis = args[0], " ".join(args[1:]); aid = f"ASM-{uuid.uuid4().hex[:10]}"; a = Assumption(aid, p.project_id, statement, basis); p.assumptions[aid] = a; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO assumptions VALUES (?, ?, ?, ?, ?)", (aid, p.project_id, statement, basis, 1), p, self._event(p.project_id, "ASSUMPTION_SET", asdict(a)))
        return self._ok(asdict(a))

    def decision_record(self, args: list[str]) -> dict:
        if len(args) < 3: raise SICLError("INVALID_ARGUMENT", "statement actor authority required")
        p = self._require_open(); statement, actor, authority = args[0], args[1], " ".join(args[2:]); did = f"DEC-{uuid.uuid4().hex[:10]}"; d = Decision(did, p.project_id, statement, actor, authority); p.decisions[did] = d; p.version += 1
        self.repo.insert_entity_and_event("INSERT INTO decisions VALUES (?, ?, ?, ?, ?, ?)", (did, p.project_id, statement, actor, authority, 1), p, self._event(p.project_id, "DECISION_RECORDED", asdict(d)))
        return self._ok(asdict(d))

    def alternative_create(self, args: list[str]) -> dict:
        if len(args) != 1:
            raise SICLError("INVALID_ARGUMENT", "alternative name required")
        p = self._require_open()
        aid = f"ALT-{uuid.uuid4().hex[:10]}"
        alternative = Alternative(aid, p.project_id, args[0])
        p.alternatives[aid] = alternative
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO alternatives VALUES (?, ?, ?, ?, ?, ?, ?)",
            (aid, p.project_id, alternative.name, alternative.description, "{}", alternative.status, alternative.version),
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

    def agent_run(self, args: list[str]) -> dict:
        if len(args) != 2 or args[0].upper() != "BIOCLIMATIC":
            raise SICLError("INVALID_ARGUMENT", "usage: /AGENT RUN BIOCLIMATIC alternative")
        p = self._require_open()
        alternative = next((item for item in p.alternatives.values() if item.alternative_id == args[1] or item.name == args[1].upper()), None)
        if alternative is None:
            raise SICLError("INVALID_ARGUMENT", f"alternative not found: {args[1]}")
        evaluation = BioclimaticAgent().evaluate(alternative, p)
        p.evaluations[evaluation.evaluation_id] = evaluation
        p.version += 1
        self.repo.insert_entity_and_event(
            "INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (evaluation.evaluation_id, evaluation.alternative_id, evaluation.objective_id, evaluation.value, evaluation.unit, evaluation.confidence, evaluation.source, evaluation.version),
            p,
            self._event(p.project_id, "AGENT_EVALUATION_RECORDED", asdict(evaluation), "EXPERT_SYSTEM"),
        )
        return self._ok({"agent": "BIOCLIMATIC", "evaluation": asdict(evaluation), "decision_created": False})

    def pareto(self, args: list[str]) -> dict:
        if len(args) != 2:
            raise SICLError("INVALID_ARGUMENT", "two objective keys required")
        p = self._project()
        objectives = [item for key in args for item in p.objectives.values() if item.key == key]
        if len(objectives) != 2:
            raise SICLError("INVALID_STATE", "both objectives with evaluations are required")
        result = pareto_front(p.alternatives.values(), p.evaluations.values(), objectives)
        return self._ok({"non_dominated": result.non_dominated, "dominated": result.dominated, "incomplete": result.incomplete, "decision_created": False})

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
