"""H-DRAW: ARKI architectural drawing engine, downstream of H-005.

Produces deterministic architectural drawing primitives and SVG sheets without
modifying H-001 through H-005 or executing external providers.
"""
from .primitives import Arc, Circle, Dimension, DimensionKind, Hatch, HatchPattern, Line, LineWeight, Point, Polyline, Rect, Text, TextAnchor
from .scale import Scale
from .paper import Margins, Orientation, PaperSize, PaperSpec
from .title_block import Specialty, TitleBlock, TitleBlockField
from .sheet import Sheet, Viewport
from .svg_export import export_sheet_svg, export_view_svg

# Historical RFC-030 exports remain available.
from .drawing_rules import DrawingRule, DrawingRuleSet, load_rule_set, validate_rule_set
from .drawing_entities import DrawingSet, DrawingSheet, DrawingView, SectionCut
from .ifc_synthetic import BIMModelSnapshot, create_synthetic_ifc, import_ifc_snapshot, validate_ifc
from .composer import compose_drawing_set
from .pdf_export import export_drawing_set
from .http_api import DrawingHttpService

__all__ = [
    "Point", "Line", "Polyline", "Rect", "Arc", "Circle", "Text", "TextAnchor", "Hatch", "HatchPattern", "Dimension", "DimensionKind", "LineWeight",
    "Scale", "PaperSize", "PaperSpec", "Margins", "Orientation", "Specialty", "TitleBlock", "TitleBlockField", "Sheet", "Viewport",
    "export_sheet_svg", "export_view_svg", "DrawingRule", "DrawingRuleSet", "load_rule_set", "validate_rule_set", "DrawingSet", "DrawingSheet",
    "DrawingView", "SectionCut", "BIMModelSnapshot", "create_synthetic_ifc", "import_ifc_snapshot", "validate_ifc", "compose_drawing_set",
    "export_drawing_set", "DrawingHttpService",
]
