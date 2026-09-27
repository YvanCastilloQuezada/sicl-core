"""Deterministic SVG exporter for Sheet and Viewport."""
from __future__ import annotations
from xml.sax.saxutils import escape
from .primitives import Dimension, Hatch, HatchPattern, Line, LineWeight, Point, Polyline, Rect, Text
from .sheet import Sheet, Viewport

_WEIGHT_STROKE_PX = {LineWeight.CUT: .70, LineWeight.HEAVY: .50, LineWeight.MEDIUM: .35, LineWeight.THIN: .25, LineWeight.HAIR: .13, LineWeight.HIDDEN: .18}
_HATCH_SVG = {HatchPattern.SOLID: ("#000", None, None), HatchPattern.EARTH: (None, "earth", 1.2), HatchPattern.CONCRETE: (None, "concrete", 1.2), HatchPattern.MASONRY: (None, "masonry", 1.0), HatchPattern.WOOD: (None, "wood", 1.0), HatchPattern.INSULATION: (None, "insulation", 1.0), HatchPattern.GLASS: (None, "glass", .8)}

def _fmt(value: float) -> str: return f"{value:.3f}"

def _line_svg(line: Line, dx: float, dy: float, scale_factor: float) -> str:
    x1, y1 = _fmt(line.start.x * scale_factor + dx), _fmt(-line.start.y * scale_factor + dy)
    x2, y2 = _fmt(line.end.x * scale_factor + dx), _fmt(-line.end.y * scale_factor + dy)
    dash = ' stroke-dasharray="4,2"' if line.dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[line.weight])}"{dash} />'

def _polyline_svg(poly: Polyline, dx: float, dy: float, scale_factor: float) -> str:
    pts = " ".join(f"{_fmt(p.x * scale_factor + dx)},{_fmt(-p.y * scale_factor + dy)}" for p in poly.points)
    tag = "polygon" if poly.closed else "polyline"
    dash = ' stroke-dasharray="4,2"' if poly.dashed else ""
    return f'<{tag} points="{pts}" fill="none" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[poly.weight])}"{dash} />'

def _rect_svg(rect: Rect, dx: float, dy: float, scale_factor: float) -> str: return _polyline_svg(rect.to_polyline(), dx, dy, scale_factor)

def _text_svg(text: Text, dx: float, dy: float, scale_factor: float) -> str:
    x, y = _fmt(text.position.x * scale_factor + dx), _fmt(-text.position.y * scale_factor + dy)
    transform = f' transform="rotate({_fmt(-text.rotation_deg)} {x} {y})"' if text.rotation_deg else ""
    return f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{_fmt(text.height_mm)}" text-anchor="{text.anchor.value}"{transform}>{escape(text.content)}</text>'

def _hatch_svg(hatch: Hatch, dx: float, dy: float, scale_factor: float) -> str:
    fill, pattern_id, _ = _HATCH_SVG[hatch.pattern]
    pts = " ".join(f"{_fmt(p.x * scale_factor + dx)},{_fmt(-p.y * scale_factor + dy)}" for p in hatch.boundary)
    return f'<polygon points="{pts}" fill="{fill if fill is not None else f"url(#{pattern_id})"}" stroke="none" />'

def _dimension_svg(dim: Dimension, dx: float, dy: float, scale_factor: float) -> str:
    parts = []
    pts = [(_fmt(p.x * scale_factor + dx), _fmt(-p.y * scale_factor + dy)) for p in dim.extension_points]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#000" stroke-width="{_fmt(_WEIGHT_STROKE_PX[LineWeight.HAIR])}" />')
    if dim.text_position is not None:
        tx, ty = _fmt(dim.text_position.x * scale_factor + dx), _fmt(-dim.text_position.y * scale_factor + dy)
        parts.append(f'<text x="{tx}" y="{ty}" font-family="sans-serif" font-size="2.0" text-anchor="middle">{escape(dim.text)}</text>')
    return "".join(parts)

def _render_element(element, dx: float, dy: float, scale_factor: float) -> str:
    if isinstance(element, Line): return _line_svg(element, dx, dy, scale_factor)
    if isinstance(element, Polyline): return _polyline_svg(element, dx, dy, scale_factor)
    if isinstance(element, Rect): return _rect_svg(element, dx, dy, scale_factor)
    if isinstance(element, Text): return _text_svg(element, dx, dy, scale_factor)
    if isinstance(element, Hatch): return _hatch_svg(element, dx, dy, scale_factor)
    if isinstance(element, Dimension): return _dimension_svg(element, dx, dy, scale_factor)
    raise TypeError(f"Unsupported element type: {type(element).__name__}")

def _hatch_defs() -> str:
    return ('<defs><pattern id="earth" width="4" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="0" y2="4" stroke="#000" stroke-width="0.15" /><line x1="0" y1="0" x2="4" y2="0" stroke="#000" stroke-width="0.15" /></pattern><pattern id="concrete" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="0.35" fill="#000" /><circle cx="4.5" cy="4.5" r="0.35" fill="#000" /></pattern><pattern id="masonry" width="6" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="6" y2="0" stroke="#000" stroke-width="0.15" /><line x1="3" y1="0" x2="3" y2="4" stroke="#000" stroke-width="0.15" /></pattern><pattern id="wood" width="4" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="4" y2="0" stroke="#000" stroke-width="0.12" /></pattern><pattern id="insulation" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0,3 Q1.5,1 3,3 T6,3" fill="none" stroke="#000" stroke-width="0.15" /></pattern><pattern id="glass" width="4" height="4" patternUnits="userSpaceOnUse"><line x1="0" y1="0" x2="4" y2="4" stroke="#000" stroke-width="0.10" /></pattern></defs>')

def export_view_svg(viewport: Viewport, width_mm: float, height_mm: float) -> str:
    body = "".join(_render_element(e, 0.0, height_mm, 1.0 / viewport.scale.denominator) for e in viewport.elements)
    return f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="{_fmt(width_mm)}mm" height="{_fmt(height_mm)}mm" viewBox="0 0 {_fmt(width_mm)} {_fmt(height_mm)}">{_hatch_defs()}{body}</svg>'

def export_sheet_svg(sheet: Sheet) -> str:
    w, h = sheet.paper.width_mm(), sheet.paper.height_mm()
    body = [f'<rect x="0" y="0" width="{_fmt(w)}" height="{_fmt(h)}" fill="#fff" stroke="none" />', f'<rect x="{_fmt(sheet.margins.left_mm)}" y="{_fmt(sheet.margins.top_mm)}" width="{_fmt(w - sheet.margins.left_mm - sheet.margins.right_mm)}" height="{_fmt(h - sheet.margins.top_mm - sheet.margins.bottom_mm)}" fill="none" stroke="#000" stroke-width="0.35" />']
    for vp in sheet.viewports:
        dx, dy = vp.origin_paper_mm
        body.append(f'<g id="viewport-{escape(vp.name)}">')
        body.extend(_render_element(element, dx, dy, 1.0 / vp.scale.denominator) for element in vp.elements)
        if vp.label_position_paper_mm is not None:
            lx, ly = vp.label_position_paper_mm
            body.append(f'<text x="{_fmt(lx)}" y="{_fmt(ly)}" font-family="sans-serif" font-size="3.5" text-anchor="middle" font-weight="bold">{escape(vp.name)} ({vp.scale.value})</text>')
        body.append('</g>')
    body.append(_render_title_block(sheet))
    return f'<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="{_fmt(w)}mm" height="{_fmt(h)}mm" viewBox="0 0 {_fmt(w)} {_fmt(h)}">{_hatch_defs()}{"".join(body)}</svg>'

def _render_title_block(sheet: Sheet) -> str:
    fields = sheet.title_block.to_fields(); w, h = sheet.paper.width_mm(), sheet.paper.height_mm(); tb_w, tb_h = 180.0, 45.0; tb_x, tb_y = w - sheet.margins.right_mm - tb_w, h - sheet.margins.bottom_mm - tb_h
    parts = [f'<rect x="{_fmt(tb_x)}" y="{_fmt(tb_y)}" width="{_fmt(tb_w)}" height="{_fmt(tb_h)}" fill="#fff" stroke="#000" stroke-width="0.5" />']
    row_h = tb_h / len(fields)
    for idx, field in enumerate(fields):
        y = tb_y + row_h * (idx + .7)
        parts.append(f'<text x="{_fmt(tb_x + 2)}" y="{_fmt(y)}" font-family="sans-serif" font-size="2.5" font-weight="bold">{escape(field.key)}</text>')
        parts.append(f'<text x="{_fmt(tb_x + 40)}" y="{_fmt(y)}" font-family="sans-serif" font-size="2.5">{escape(field.value)}</text>')
    return "".join(parts)
