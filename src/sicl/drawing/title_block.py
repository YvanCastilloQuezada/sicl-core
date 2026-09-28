"""Peruvian architecture title block contract with RFC-030 compatibility."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

REQUIRED_FIELDS = ("project", "sheet", "title", "scale", "date", "author", "revision", "status")

class Specialty(str, Enum):
    ARCHITECTURE = "ARQUITECTURA"
    STRUCTURE = "ESTRUCTURAS"
    MEP_SANITARY = "INSTALACIONES SANITARIAS"
    MEP_ELECTRICAL = "INSTALACIONES ELECTRICAS"
    MEP_HVAC = "INSTALACIONES MECANICAS"
    FIRE_PROTECTION = "SEGURIDAD CONTRA INCENDIOS"
    SITE = "UBICACION Y EMPLAZAMIENTO"

@dataclass(frozen=True)
class TitleBlockField:
    key: str
    value: str
    required: bool = True
    def __post_init__(self) -> None:
        if self.required and not self.value:
            raise ValueError(f"Title block field '{self.key}' is required")

@dataclass(frozen=True)
class TitleBlock:
    project_name: str
    project_location: str
    owner: str
    specialty: Specialty
    architect_name: str
    cap_number: str
    drawing_number: str
    revision: str = "A"
    date_iso: str = ""
    notes: tuple[str, ...] = field(default_factory=tuple)
    def __post_init__(self) -> None:
        required = [self.project_name, self.project_location, self.owner, self.architect_name, self.cap_number, self.drawing_number, self.revision]
        if not all(v and str(v).strip() for v in required):
            raise ValueError("Title block has empty required fields")
        if self.date_iso:
            self._validate_iso_date(self.date_iso)
    @staticmethod
    def _validate_iso_date(value: str) -> None:
        if len(value) != 10 or value[4] != "-" or value[7] != "-":
            raise ValueError("date_iso must be YYYY-MM-DD")
        y, m, d = value[0:4], value[5:7], value[8:10]
        if not (y.isdigit() and m.isdigit() and d.isdigit()):
            raise ValueError("date_iso must be YYYY-MM-DD")
        if not (1 <= int(m) <= 12 and 1 <= int(d) <= 31):
            raise ValueError("date_iso has invalid month/day")
    def to_fields(self) -> tuple[TitleBlockField, ...]:
        base = [TitleBlockField("PROYECTO", self.project_name), TitleBlockField("UBICACION", self.project_location), TitleBlockField("PROPIETARIO", self.owner), TitleBlockField("ESPECIALIDAD", self.specialty.value), TitleBlockField("ARQUITECTO", self.architect_name), TitleBlockField("CAP", self.cap_number), TitleBlockField("LAMINA", self.drawing_number), TitleBlockField("REVISION", self.revision)]
        if self.date_iso:
            base.append(TitleBlockField("FECHA", self.date_iso, required=False))
        return tuple(base)

def peru_title_block(project: str, sheet: str, title: str, scale: str = "1:50") -> dict:
    block = {"project": project, "sheet": sheet, "title": title, "scale": scale, "date": "2026-09-26", "author": "SICL / ARKI", "revision": "R00", "status": "DRAFT"}
    missing = [key for key in REQUIRED_FIELDS if not block.get(key)]
    if missing:
        raise ValueError(f"missing title block fields: {missing}")
    return {**block, "format": "A3", "dimensions_mm": {"width": 180, "height": 60}}
