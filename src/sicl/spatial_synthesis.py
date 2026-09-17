from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping

from .spatial import SpatialElement, SpatialRepresentation, spatial_element_id
from .domain import SpatialScope


RELATION_TYPES = ("ADJACENT_TO", "NEAR", "SEPARATE_FROM", "CONNECTED_TO", "ACCESS_FROM")


@dataclass(frozen=True)
class ProgramSpaceRequirement:
    id: str
    project_id: str
    name: str
    space_type: str
    quantity: int
    area_range: tuple[float, float]
    priority: str
    required: bool
    provenance: str = "SYNTHETIC / DEMONSTRATION DATA"
    status: str = "DECLARED"


@dataclass(frozen=True)
class ArchitecturalProgram:
    id: str
    project_id: str
    requirements: tuple[ProgramSpaceRequirement, ...]
    provenance: str = "SYNTHETIC / DEMONSTRATION DATA"

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "project_id": self.project_id, "requirements": [asdict(item) for item in self.requirements], "provenance": self.provenance}


@dataclass(frozen=True)
class SpatialRelationship:
    id: str
    source_requirement_id: str
    target_requirement_id: str
    relationship_type: str
    strength: str
    provenance: str = "PROGRAM_DECLARED"
    satisfaction: str = "UNKNOWN"


@dataclass(frozen=True)
class SpatialGraph:
    id: str
    program_id: str
    nodes: tuple[str, ...]
    edges: tuple[SpatialRelationship, ...]

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "program_id": self.program_id, "nodes": list(self.nodes), "edges": [asdict(edge) for edge in self.edges]}


def demo_program(project_id: str = "UPAO-001") -> ArchitecturalProgram:
    reqs = (
        ProgramSpaceRequirement("PRG-ENTRY", project_id, "Acceso principal", "ENTRY", 1, (18.0, 28.0), "HIGH", True),
        ProgramSpaceRequirement("PRG-COMMON", project_id, "Espacio común", "COMMON", 1, (90.0, 130.0), "HIGH", True),
        ProgramSpaceRequirement("PRG-CLASS", project_id, "Aula flexible", "LEARNING", 2, (42.0, 60.0), "HIGH", True),
        ProgramSpaceRequirement("PRG-ADMIN", project_id, "Administración", "ADMIN", 1, (24.0, 40.0), "MEDIUM", False),
        ProgramSpaceRequirement("PRG-SERVICE", project_id, "Servicios", "SERVICE", 1, (18.0, 30.0), "MEDIUM", True),
    )
    return ArchitecturalProgram(f"PROGRAM-{project_id}", project_id, reqs)


def build_spatial_graph(program: ArchitecturalProgram) -> SpatialGraph:
    ids = tuple(req.id for req in program.requirements)
    edges = (
        SpatialRelationship("REL-ENTRY-COMMON", "PRG-ENTRY", "PRG-COMMON", "ACCESS_FROM", "REQUIRED"),
        SpatialRelationship("REL-COMMON-CLASS", "PRG-COMMON", "PRG-CLASS", "ADJACENT_TO", "REQUIRED"),
        SpatialRelationship("REL-CLASS-ADMIN", "PRG-CLASS", "PRG-ADMIN", "NEAR", "PREFERRED"),
        SpatialRelationship("REL-SERVICE-COMMON", "PRG-SERVICE", "PRG-COMMON", "SEPARATE_FROM", "REQUIRED"),
        SpatialRelationship("REL-ENTRY-SERVICE", "PRG-ENTRY", "PRG-SERVICE", "CONNECTED_TO", "PREFERRED"),
    )
    return SpatialGraph(f"GRAPH-{program.project_id}", program.id, ids, edges)


def _rect(x: float, y: float, width: float, height: float) -> dict[str, Any]:
    return {"type": "polygon", "coordinates": [[[x, y], [x + width, y], [x + width, y + height], [x, y + height], [x, y]]]}


def generate_space_layout(program: ArchitecturalProgram, graph: SpatialGraph, alternative_id: str, family: str = "COURTYARD") -> dict[str, Any]:
    family = family.upper()
    placements = {
        "CENTRALIZED": [(8, 8), (28, 8), (48, 8), (28, 25), (8, 25)],
        "LINEAR": [(8, 8), (28, 8), (48, 8), (68, 8), (88, 8)],
        "COURTYARD": [(8, 8), (32, 8), (56, 8), (32, 30), (8, 30)],
        "CLUSTERED": [(12, 10), (30, 14), (48, 10), (24, 32), (48, 32)],
    }
    points = placements.get(family, placements["COURTYARD"])
    elements: list[SpatialElement] = []
    for index, req in enumerate(program.requirements):
        x, y = points[index]
        width, height = (12.0, 8.0)
        if req.space_type == "COMMON": width, height = (18.0, 12.0)
        if req.space_type == "LEARNING": width, height = (14.0, 10.0)
        if req.space_type == "ADMIN": width, height = (10.0, 8.0)
        for repeat in range(req.quantity):
            key = f"{req.id}-{repeat + 1}"
            sid = spatial_element_id(alternative_id, "SPACE", key, generator_version="P3-SPACE-1")
            elements.append(SpatialElement(sid, "SPATIAL_ZONE", _rect(x + repeat * 2, y + repeat * 2, width, height), labels={"name": req.name, "space_type": req.space_type}, metadata={"program_requirement_id": req.id, "area_range": list(req.area_range), "generated_area_m2": width * height, "generation_operation": "GENERATE_SPACE_LAYOUT", "family": family, "provenance": req.provenance, "status": "GENERATED"}))
    access_id = spatial_element_id(alternative_id, "CIRCULATION", "MAIN-PATH", generator_version="P3-SPACE-1")
    elements.append(SpatialElement(access_id, "CIRCULATION_ELEMENT", _rect(5, 20, 100, 2), labels={"name": "Circulación principal"}, metadata={"connectivity": "ENTRY_TO_COMMON_TO_LEARNING", "provenance": "DETERMINISTIC_SYNTHESIS"}))
    fingerprint = hashlib.sha256(json.dumps({"program": program.to_dict(), "graph": graph.to_dict(), "alternative_id": alternative_id, "family": family}, sort_keys=True).encode()).hexdigest()
    representation = SpatialRepresentation(f"SR-P3-{alternative_id}", alternative_id, SpatialScope.EDIFICACION, "P3-SPACE-1", "P3-DETERMINISTIC", "LOCAL_ENU", "m", fingerprint, seed=f"P3:{family}", elements=tuple(elements), north_degrees=0.0)
    representation.validate()
    return {"representation": representation.to_dict(), "space_ids": [item.id for item in elements if item.element_type == "SPATIAL_ZONE"], "circulation_ids": [access_id], "family": family, "program_id": program.id, "graph_id": graph.id, "lineage": {"parent": "BASE_PROGRAM", "operation": "GENERATE_SPACE_LAYOUT", "alternative_id": alternative_id}, "relationship_evaluation": [{"relationship_id": edge.id, "state": "UNKNOWN", "reason": "Generated layout requires geometric validation"} for edge in graph.edges], "validation": "GENERATED_LAYOUT_NOT_VALIDATED"}


def synthesize_form_space(program: ArchitecturalProgram, graph: SpatialGraph, alternatives: list[dict[str, Any]]) -> dict[str, Any]:
    return {"program": program.to_dict(), "spatial_graph": graph.to_dict(), "alternatives": alternatives, "lineage": {"intent": "HUMAN_CONFIRMED", "program_to_graph": True, "graph_to_space": True, "space_to_alternative": True}, "automatic_winner": False, "decision_created": False, "provenance": "GDI-P3 deterministic architectural spatial synthesis"}

__all__ = ["ArchitecturalProgram", "ProgramSpaceRequirement", "SpatialRelationship", "SpatialGraph", "demo_program", "build_spatial_graph", "generate_space_layout", "synthesize_form_space", "RELATION_TYPES"]
