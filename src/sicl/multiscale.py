from __future__ import annotations

from enum import Enum

from .domain import SpatialScope


SCALE_ORDER = (
    SpatialScope.PAIS,
    SpatialScope.MACRO_REGION,
    SpatialScope.REGION,
    SpatialScope.PROVINCIA_METROPOLI,
    SpatialScope.DISTRITO_CIUDAD,
    SpatialScope.ZONA_BARRIO_SECTOR,
    SpatialScope.PARCELA_SITIO,
    SpatialScope.EDIFICACION,
    SpatialScope.SISTEMA,
    SpatialScope.ESPACIO,
    SpatialScope.OBJETO,
)


class ScaleRelationType(str, Enum):
    CONTAINS = "CONTAINS"
    OVERLAPS = "OVERLAPS"
    INFLUENCES = "INFLUENCES"
    DEPENDS_ON = "DEPENDS_ON"


def _scope(value: SpatialScope | str) -> SpatialScope:
    return value if isinstance(value, SpatialScope) else SpatialScope(value.lower())


def parent_scope(scope: SpatialScope | str) -> SpatialScope | None:
    value = _scope(scope)
    index = SCALE_ORDER.index(value)
    return SCALE_ORDER[index - 1] if index else None


def children_scopes(scope: SpatialScope | str) -> list[SpatialScope]:
    value = _scope(scope)
    index = SCALE_ORDER.index(value)
    return [SCALE_ORDER[index + 1]] if index + 1 < len(SCALE_ORDER) else []


def is_ancestor(a: SpatialScope | str, b: SpatialScope | str) -> bool:
    left, right = _scope(a), _scope(b)
    while (right := parent_scope(right)) is not None:
        if right == left:
            return True
    return False


def is_descendant(a: SpatialScope | str, b: SpatialScope | str) -> bool:
    return is_ancestor(b, a)


def compatible_scopes(a: SpatialScope | str, b: SpatialScope | str) -> bool:
    left, right = _scope(a), _scope(b)
    return left == right or is_ancestor(left, right) or is_ancestor(right, left)
