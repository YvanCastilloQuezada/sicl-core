"""Deterministic SVG exporter for Sheet and Viewport."""
from __future__ import annotations
from html import escape
import math
from .primitives import Arc, Circle, Dimension, Hatch, HatchPattern, Line, LineWeight, Point, Polyline, Rect, Text
from .sheet import Sheet, Viewport

_WEIGHT_STROKE_PX = {LineWeight.CUT: .70, LineWeight.HEAVY: .50, LineWeight.MEDIUM: .35, LineWeight.THIN: .25, LineWeight.HAIR: .13, LineWeight.HIDDEN: .18}
_HATCH_SVG = {HatchPattern.SOLID: ("#000", None), HatchPattern.EARTH: (None, "earth"), HatchPattern.CONCRETE: (None, "concrete"), HatchPattern.MASONRY: (None, "masonry"), HatchPattern.WOOD: (None, "wood"), HatchPattern.INSULATION: (None, "insulation"), HatchPattern.GLASS: (None, "glass")}

def _fmt(value: float) -> str: return f"{value:.3f}"

def _metadata_attrs(element) -> str:
    attrs = [f'data-layer="{escape(element.layer, quote=True)}"']
    for name, key in (("primitive_id", "data-primitive-id"), ("semantic_role", "data-semantic-role"), ("source_ref", "data-source-ref")):
        value = getattr(element, name, None)
        if value is not None:
            attrs.append(f'{key}="{escape(str(value), quote=True)}"')
    return " " + " ".join(attrs)

def _xy(point: Point, dx: float, dy: float, scale_factor: float) -> tuple[str, str]:
    return _fmt(point.x * scale_factor + dx), _fmt(-point.y * scale_factor + dy)

def _line_svg(line: Line, dx: float, dy: float, scale_factor: float) -> str:
    x1, y1 = _xy(line.start, dx, dy, scale_factor); x2, y2 = _xy(line.end, dx, dy, scale_factor)
    dash = ' stroke-dasharray="4,2"' if line.dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[line.weight])}"{dash}{_metadata_attrs(line)} />'

def _polyline_svg(poly: Polyline, dx: float, dy: float, scale_factor: float) -> str:
    pts = " ".join(f"{x},{y}" for x, y in (_xy(p, dx, dy, scale_factor) for p in poly.points))
    tag = "polygon" if poly.closed else "polyline"; dash = ' stroke-dasharray="4,2"' if poly.dashed else ""
    return f'<{tag} points="{pts}" fill="none" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[poly.weight])}"{dash}{_metadata_attrs(poly)} />'

def _rect_svg(rect: Rect, dx: float, dy: float, scale_factor: float) -> str:
    return _polyline_svg(rect.to_polyline(), dx, dy, scale_factor)

def _circle_svg(circle: Circle, dx: float, dy: float, scale_factor: float) -> str:
    cx, cy = _xy(circle.center, dx, dy, scale_factor)
    return f'<circle cx="{cx}" cy="{cy}" r="{_fmt(circle.radius * scale_factor)}" fill="none" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[circle.weight])}"{_metadata_attrs(circle)} />'

def _arc_svg(arc: Arc, dx: float, dy: float, scale_factor: float) -> str:
    start = math.radians(arc.start_deg); end = math.radians(arc.end_deg)
    p1 = Point(arc.center.x + arc.radius * math.cos(start), arc.center.y + arc.radius * math.sin(start))
    p2 = Point(arc.center.x + arc.radius * math.cos(end), arc.center.y + arc.radius * math.sin(end))
    x1, y1 = _xy(p1, dx, dy, scale_factor); x2, y2 = _xy(p2, dx, dy, scale_factor)
    delta = (arc.end_deg - arc.start_deg) % 360; large = 1 if delta > 180 else 0
    return f'<path d="M {x1} {y1} A {_fmt(arc.radius * scale_factor)} {_fmt(arc.radius * scale_factor)} 0 {large} 0 {x2} {y2}" fill="none" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[arc.weight])}"{_metadata_attrs(arc)} />'

def _text_svg(text: Text, dx: float, dy: float, scale_factor: float) -> str:
    x, y = _xy(text.position, dx, dy, scale_factor)
    transform = f' transform="rotate({_fmt(-text.rotation_deg)} {x} {y})"' if text.rotation_deg else ""
    return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{_fmt(text.height_mm)}" text-anchor="{text.anchor.value}"{transform}{_metadata_attrs(text)}>{escape(text.content)}</text>'

def _hatch_svg(hatch: Hatch, dx: float, dy: float, scale_factor: float) -> str:
    fill, pattern_id = _HATCH_SVG[hatch.pattern]
    pts = " ".join(f"{x},{y}" for x, y in (_xy(p, dx, dy, scale_factor) for p in hatch.boundary))
    return f'<polygon points="{pts}" fill="{fill if fill is not None else f"url(#{pattern_id})"}" stroke="none"{_metadata_attrs(hatch)} />'

def _dimension_svg(dim: Dimension, dx: float, dy: float, scale_factor: float) -> str:
    parts = []; pts = [_xy(p, dx, dy, scale_factor) for p in dim.extension_points]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[LineWeight.HAIR])}"{_metadata_attrs(dim)} />')
    x1, y1 = pts[0]; x2, y2 = pts[-1]
    parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[LineWeight.THIN])}" marker-start="url(#dim-arrow)" marker-end="url(#dim-arrow)" data-dimension-kind="{dim.kind.value}"{_metadata_attrs(dim)} />')
    position = dim.text_position or Point((dim.extension_points[0].x + dim.extension_points[-1].x) / 2, (dim.extension_points[0].y + dim.extension_points[-1].y) / 2)
    tx, ty = _xy(position, dx, dy, scale_factor)
    parts.append(f'<text x="{tx}" y="{ty}" font-family="sans-serif" font-size="2.0" text-anchor="middle" data-dimension-kind="{dim.kind.value}"{_metadata_attrs(dim)}>{escape(dim.text)}</text>')
    return "".join(parts)

def _render_element(element, dx: float, dy: float, scale_factor: float) -> str:
    if isinstance(element, Line): return _line_svg(element, dx, dy, scale_factor)
    if isinstance(element, Polyline): return _polyline_svg(element, dx, dy, scale_factor)
    if isinstance(element, Rect): return _rect_svg(element, dx, dy, scale_factor)
    if isinstance(element, Circle): return _circle_svg(element, dx, dy, scale_factor)
    if isinstance(element, Arc): return _arc_svg(element, dx, dy, scale_factor)
    if isinstance(element, Text): return _text_svg(element, dx, dy, scale_factor)
    if isinstance(element, Hatch): return _hatch_svg(element, dx, dy, scale_factor)
    if isinstance(element, Dimension): return _dimension_svg(element, dx, dy, scale_factor)
    raise TypeError(f"Unsupported element type: {type(element).__name__}")

def _hatch_defs() -> str:
    return ('<defs><marker id="dim-arrow" markerWidth="5" markerHeight="5" refX="4" refY="2.5" orient="auto"><path d="M 5 0 L 0 2.5 L 5 5 z" fill="#000" /></marker><pattern id="earth" width="4" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="0" y2="4" stroke="#000" stroke-width="0.15" /><line x1="0" y1="0" x2="4" y2="0" stroke="#000" stroke-width="0.15" /></pattern><pattern id="concrete" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="0.35" fill="#000" /><circle cx="4.5" cy="4.5" r="0.35" fill="#000" /></pattern><pattern id="masonry" width="6" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="6" y2="0" stroke="#000" stroke-width="0.15" /><line x1="3" y1="0" x2="3" y2="4" stroke="#000" stroke-width="0.15" /></pattern><pattern id="wood" width="4" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="4" y2="0" stroke="#000" stroke-width="0.12" /></pattern><pattern id="insulation" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,3 Q1.5,1 3,3 T6,3" fill="none" stroke="#000" stroke-width="0.15" /></pattern><pattern id="glass" width="4" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="4" y2="4" stroke="#000" stroke-width="0.10" /></pattern></defs>')

def _layer_groups(elements, dx: float, dy: float, scale_factor: float) -> list[str]:
    groups: dict[str, list[str]] = {}
    for element in elements:
        groups.setdefault(element.layer, []).append(_render_element(element, dx, dy, scale_factor))
    return [f'<g id="layer-{escape(layer, quote=True)}" data-layer="{escape(layer, quote=True)}">{"".join(parts)}</g>' for layer, parts in groups.items()]

def _viewport_bbox(viewport: Viewport) -> tuple[float, float, float, float] | None:
    points = []; scale = 1.0 / viewport.scale.denominator
    for element in viewport.elements:
        if isinstance(element, (Line, Circle, Arc)):
            points.extend((Point(element.center.x - element.radius, element.center.y - element.radius), Point(element.center.x + element.radius, element.center.y + element.radius)) if isinstance(element, (Circle, Arc)) else (element.start, element.end))
        elif isinstance(element, Polyline): points.extend(element.points)
        elif isinstance(element, Rect): points.extend(element.corners())
        elif isinstance(element, Hatch): points.extend(element.boundary)
        elif isinstance(element, Dimension): points.extend(element.extension_points)
        elif isinstance(element, Text): points.append(element.position)
    if not points: return None
    x0, x1 = min(p.x for p in points) * scale + viewport.origin_paper_mm[0], max(p.x for p in points) * scale + viewport.origin_paper_mm[0]
    y0, y1 = viewport.origin_paper_mm[1] - max(p.y for p in points) * scale, viewport.origin_paper_mm[1] - min(p.y for p in points) * scale
    return x0, y0, x1, y1

def _validate_title_block_collision(sheet: Sheet) -> None:
    w, h = sheet.paper.width_mm(), sheet.paper.height_mm(); tb = (w - sheet.margins.right_mm - 180.0, h - sheet.margins.bottom_mm - 45.0, w - sheet.margins.right_mm, h - sheet.margins.bottom_mm)
    for viewport in sheet.viewports:
        box = _viewport_bbox(viewport)
        if box is not None and box[0] < tb[2] and box[2] > tb[0] and box[1] < tb[3] and box[3] > tb[1]:
            raise ValueError(f"viewport/title-block collision: {viewport.name}")

def export_view_svg(viewport: Viewport, width_mm: float, height_mm: float) -> str:
    body = "".join(_layer_groups(viewport.elements, 0.0, height_mm, 1.0 / viewport.scale.denominator))
    return f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="{_fmt(width_mm)}mm" height="{_fmt(height_mm)}mm" viewBox="0 0 {_fmt(width_mm)} {_fmt(height_mm)}">{_hatch_defs()}{body}</svg>'

def export_sheet_svg(sheet: Sheet) -> str:
    _validate_title_block_collision(sheet); w, h = sheet.paper.width_mm(), sheet.paper.height_mm()
    body = [f'<rect x="0" y="0" width="{_fmt(w)}" height="{_fmt(h)}" fill="#fff" stroke="none" />', f'<rect x="{_fmt(sheet.margins.left_mm)}" y="{_fmt(sheet.margins.top_mm)}" width="{_fmt(w - sheet.margins.left_mm - sheet.margins.right_mm)}" height="{_fmt(h - sheet.margins.top_mm - sheet.margins.bottom_mm)}" fill="none" stroke="#000" stroke-width="0.35" />']
    for vp in sheet.viewports:
        dx, dy = vp.origin_paper_mm; body.append(f'<g id="viewport-{escape(vp.name, quote=True)}" data-viewport="{escape(vp.name, quote=True)}">'); body.extend(_layer_groups(vp.elements, dx, dy, 1.0 / vp.scale.denominator))
        if vp.label_position_paper_mm is not None:
            lx, ly = vp.label_position_paper_mm; body.append(f'<text x="{_fmt(lx)}" y="{_fmt(ly)}" font-family="sans-serif" font-size="3.5" text-anchor="middle" font-weight="bold">{escape(vp.name)} ({vp.scale.value})</text>')
        body.append('</g>')
    body.append(_render_title_block(sheet))
    return f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="{_fmt(w)}mm" height="{_fmt(h)}mm" viewBox="0 0 {_fmt(w)} {_fmt(h)}">{_hatch_defs()}'+"".join(body)+'</svg>'

def _render_title_block(sheet: Sheet) -> str:
    fields = sheet.title_block.to_fields(); w, h = sheet.paper.width_mm(), sheet.paper.height_mm(); tb_w, tb_h = 180.0, 45.0; tb_x, tb_y = w - sheet.margins.right_mm - tb_w, h - sheet.margins.bottom_mm - tb_h
    parts = [f'<rect x="{_fmt(tb_x)}" y="{_fmt(tb_y)}" width="{_fmt(tb_w)}" height="{_fmt(tb_h)}" fill="#fff" stroke="#000" stroke-width="0.5" data-layer="title-block" />']; row_h = tb_h / len(fields)
    for idx, field in enumerate(fields):
        y = tb_y + row_h * (idx + .7); parts.append(f'<text x="{_fmt(tb_x + 2)}" y="{_fmt(y)}" font-family="sans-serif" font-size="2.5" font-weight="bold" data-layer="title-block">{escape(field.key)}</text>'); parts.append(f'<text x="{_fmt(tb_x + 40)}" y="{_fmt(y)}" font-family="sans-serif" font-size="2.5" data-layer="title-block">{escape(field.value)}</text>')
    return "".join(parts)
