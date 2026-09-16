from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class PrincipleCategory(str, Enum):
    PROPORCION = "PROPORCION"
    ESCALA = "ESCALA"
    RITMO = "RITMO"
    JERARQUIA = "JERARQUIA"
    EQUILIBRIO = "EQUILIBRIO"
    CONTRASTE = "CONTRASTE"
    UNIDAD = "UNIDAD"
    SECUENCIA = "SECUENCIA"
    LUZ = "LUZ"
    MATERIALIDAD = "MATERIALIDAD"
    TEXTURA = "TEXTURA"
    LLENO_VACIO = "LLENO_VACIO"
    INTEGRACION = "INTEGRACION"
    CONTEXTO = "CONTEXTO"
    PERCEPCION = "PERCEPCION"
    ERGONOMIA = "ERGONOMIA"


@dataclass(frozen=True)
class DesignPrinciple:
    principle_id: str
    name: str
    category: PrincipleCategory
    description: str
    applicable_scopes: list[str]
    source: str


@dataclass(frozen=True)
class Referent:
    referent_id: str
    name: str
    author: str | None
    year: int | None
    location: str | None
    discipline: str
    description: str
    principles_demonstrated: list[str]
    source: str


_ALL_SCOPES = [
    "pais", "region", "provincia_metropoli", "ciudad_distrito",
    "barrio_sector", "parcela_sitio", "edificio", "espacio", "objeto",
]


# Fuentes bibliográficas reales; no se incluyen entradas PENDING_REFERENCE.
PRINCIPLES: tuple[DesignPrinciple, ...] = (
    DesignPrinciple("P-01", "Proporción", PrincipleCategory.PROPORCION, "Relación armónica entre dimensiones y partes de una composición.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-02", "Escala", PrincipleCategory.ESCALA, "Relación dimensional de un elemento con el cuerpo humano, otros elementos y su entorno.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-03", "Ritmo", PrincipleCategory.RITMO, "Repetición modulada que establece continuidad y movimiento perceptual.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-04", "Jerarquía", PrincipleCategory.JERARQUIA, "Orden relativo de importancia visual, espacial y funcional entre partes.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-05", "Equilibrio", PrincipleCategory.EQUILIBRIO, "Distribución compensada de pesos visuales, espaciales o compositivos.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-06", "Contraste", PrincipleCategory.CONTRASTE, "Diferenciación controlada de elementos para establecer énfasis y legibilidad.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-07", "Unidad", PrincipleCategory.UNIDAD, "Coherencia perceptual y conceptual que integra las partes en un conjunto reconocible.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-08", "Secuencia", PrincipleCategory.SECUENCIA, "Orden de percepción y experiencia producido por la sucesión de espacios o elementos.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-09", "Luz", PrincipleCategory.LUZ, "Uso intencional de iluminación natural y artificial para configurar espacio y percepción.", ["edificio", "espacio", "objeto"], "Zumthor, Peter (2006), Atmospheres: Architectural Environments, Surrounding Objects, Birkhäuser."),
    DesignPrinciple("P-10", "Materialidad", PrincipleCategory.MATERIALIDAD, "Reconocimiento de las propiedades, expresión y comportamiento de los materiales en el diseño.", ["parcela_sitio", "edificio", "espacio", "objeto"], "Zumthor, Peter (2010), Thinking Architecture, 3rd ed., Birkhäuser."),
    DesignPrinciple("P-11", "Textura", PrincipleCategory.TEXTURA, "Cualidad superficial táctil y visual que contribuye a la experiencia del elemento o espacio.", ["edificio", "espacio", "objeto"], "Zumthor, Peter (2006), Atmospheres: Architectural Environments, Surrounding Objects, Birkhäuser."),
    DesignPrinciple("P-12", "Lleno-vacío", PrincipleCategory.LLENO_VACIO, "Relación compositiva entre masa construida, vacío espacial y campo de percepción.", _ALL_SCOPES, "Ching, Francis D. K. (2014), Architecture: Form, Space, and Order, 4th ed., Wiley."),
    DesignPrinciple("P-13", "Integración", PrincipleCategory.INTEGRACION, "Relación deliberada entre una intervención y las condiciones físicas, sociales y espaciales de su entorno.", ["ciudad_distrito", "barrio_sector", "parcela_sitio", "edificio", "espacio"], "Alexander, Christopher et al. (1977), A Pattern Language, Oxford University Press."),
    DesignPrinciple("P-14", "Contexto", PrincipleCategory.CONTEXTO, "Reconocimiento de las condiciones culturales, territoriales e históricas que informan el diseño.", ["region", "provincia_metropoli", "ciudad_distrito", "barrio_sector", "parcela_sitio", "edificio"], "Norberg-Schulz, Christian (1980), Genius Loci: Towards a Phenomenology of Architecture, Rizzoli."),
    DesignPrinciple("P-15", "Ergonomía", PrincipleCategory.ERGONOMIA, "Adaptación dimensional y funcional del entorno construido a las capacidades y actividades humanas.", ["edificio", "espacio", "objeto"], "Neufert, Ernst (2012), Architects' Data, 4th ed., Wiley-Blackwell."),
)

REFERENTS: tuple[Referent, ...] = ()


def _public(principle: DesignPrinciple) -> dict[str, Any]:
    value = asdict(principle)
    value["category"] = principle.category.value
    return value


def list_principles(category: str | None = None) -> list[dict[str, Any]]:
    values = PRINCIPLES
    if category:
        normalized = category.upper()
        values = tuple(item for item in values if item.category.value == normalized)
    return [_public(item) for item in values if item.source != "PENDING_REFERENCE"]


def get_principle(principle_id: str) -> dict[str, Any] | None:
    item = next((item for item in PRINCIPLES if item.principle_id == principle_id), None)
    if item is None or item.source == "PENDING_REFERENCE":
        return None
    return _public(item)
