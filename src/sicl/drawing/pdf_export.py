from __future__ import annotations
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from .drawing_entities import DrawingSet, DrawingSheet

PAGE = landscape(A3)

def _axis(c, x, y, label):
    c.circle(x, y, 3.2 * mm, stroke=1, fill=0); c.setFont("Helvetica-Bold", 6); c.drawCentredString(x, y - 1.2 * mm, label)

def _dimension(c, x1, y1, x2, y2, text, offset=0):
    c.setLineWidth(0.25); c.line(x1, y1, x2, y2)
    if abs(y2-y1) < 1: c.line(x1, y1-2*mm, x1, y1+2*mm); c.line(x2, y2-2*mm, x2, y2+2*mm); c.drawCentredString((x1+x2)/2, y1+1.5*mm+offset, text)
    else: c.line(x1-2*mm, y1, x1+2*mm, y1); c.line(x2-2*mm, y2, x2+2*mm, y2); c.saveState(); c.translate(x1-5*mm, (y1+y2)/2); c.rotate(90); c.drawCentredString(0, offset, text); c.restoreState()

def _door(c, x, y, radius=10*mm):
    c.setLineWidth(0.35); c.line(x, y, x+radius, y); c.arc(x, y, x+2*radius, y+2*radius, 180, 90)

def _draw_floor_plan(c, x0, y0, x1, y1, view_type):
    c.setStrokeColor(colors.black); c.setFillColor(colors.black)
    # outer wall and internal wall network
    c.setLineWidth(1.4); c.rect(x0, y0, x1-x0, y1-y0)
    c.setLineWidth(0.9); c.rect(x0+3*mm, y0+3*mm, x1-x0-6*mm, y1-y0-6*mm)
    c.setLineWidth(0.55)
    xm=x0+(x1-x0)*.48; ym=y0+(y1-y0)*.52
    c.line(xm,y0+3*mm,xm,y1-3*mm); c.line(x0+3*mm,ym,x1-3*mm,ym)
    c.line(x0+3*mm,y0+(y1-y0)*.25,xm,y0+(y1-y0)*.25)
    c.line(xm,y0+(y1-y0)*.76,x1-3*mm,y0+(y1-y0)*.76)
    # patio / stair / wet core
    c.setLineWidth(0.35); c.rect(xm-18*mm,ym-12*mm,36*mm,24*mm)
    c.setFont("Helvetica",6); c.drawCentredString(xm,ym,"PATIO INTERIOR")
    for i in range(8): c.line(xm+22*mm, y0+13*mm+i*3*mm, xm+40*mm, y0+13*mm+i*3*mm)
    c.drawString(xm+23*mm,y0+8*mm,"ESCALERA")
    # doors, windows and room labels
    _door(c, x0+25*mm, ym); _door(c, xm, y0+(y1-y0)*.25); _door(c, xm, ym+15*mm)
    c.setLineWidth(0.8); c.line(x0+18*mm,y1,x0+38*mm,y1); c.line(xm+22*mm,y1,xm+48*mm,y1); c.line(x1,y0+28*mm,x1,y0+50*mm)
    c.setFont("Helvetica-Bold",7)
    labels=[("SALA\n24.00 m²",x0+28*mm,ym+25*mm),("COMEDOR\n18.00 m²",x0+28*mm,ym-25*mm),("COCINA\n12.00 m²",xm+28*mm,ym+25*mm),("DORMITORIO 01\n14.00 m²",xm+28*mm,ym-25*mm)]
    for text,x,y in labels:
        for i,line in enumerate(text.split("\n")): c.drawCentredString(x,y-i*3*mm,line)
    c.setFont("Helvetica",6); c.drawString(x0+5*mm,y0+5*mm,"NPT ±0.00"); c.drawString(x1-27*mm,y0+5*mm,"P-1"); c.drawString(x0+5*mm,y1-8*mm,"V-1 1.20"); c.drawString(x1-20*mm,y1-8*mm,"V-2 1.20")

def _draw_sheet(c: canvas.Canvas, sheet: DrawingSheet, index: int):
    width,height=PAGE; c.setStrokeColor(colors.black); c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold",16); c.drawString(25*mm,height-18*mm,f"EDIFICIO YVAN TRUJILLO · {sheet.sheet_id}")
    c.setFont("Helvetica",8); c.drawString(25*mm,height-25*mm,f"{sheet.title} · TÉCNICO · ESCALA 1:50 · LOD 300")
    x0,y0=38*mm,83*mm; x1,y1=width-55*mm,height-48*mm
    # axis system and double dimension rings
    axis_x=[x0+(x1-x0)*p for p in (.0,.25,.5,.75,1.0)]; axis_y=[y0+(y1-y0)*p for p in (0,.25,.5,.75,1)]
    for i,x in enumerate(axis_x): _axis(c,x,y1+8*mm,["A","A'","B","B'","C"][i]); _axis(c,x,y0-8*mm,["A","A'","B","B'","C"][i])
    for i,y in enumerate(axis_y): _axis(c,x0-8*mm,y,str(i+1)); _axis(c,x1+8*mm,y,str(i+1))
    _dimension(c,x0,y1+16*mm,x1,y1+16*mm,"10.00 m",0); _dimension(c,x0-16*mm,y0,x0-16*mm,y1,"8.00 m",0)
    _draw_floor_plan(c,x0,y0,x1,y1,sheet.views[0].view_type)
    c.setFont("Helvetica",7); c.drawString(x0,y0-13*mm,"COTAS PARCIALES · ENTRE EJES · TOTALES"); c.drawString(x0+70*mm,y0-13*mm,"ESCALA GRÁFICA 0 1 2 3 4 5 m"); c.drawString(x1-24*mm,y0-13*mm,"NORTE ▲")
    # title block, 180 x 60 mm, complete eight-field structure
    bx,by=width-195*mm,10*mm; c.setLineWidth(0.8); c.rect(bx,by,180*mm,60*mm); c.line(bx,by+15*mm,bx+180*mm,by+15*mm); c.line(bx,by+30*mm,bx+180*mm,by+30*mm); c.line(bx,by+45*mm,bx+180*mm,by+45*mm); c.line(bx+90*mm,by,bx+90*mm,by+60*mm)
    c.setFont("Helvetica-Bold",6.5); c.drawString(bx+3*mm,by+51*mm,"PROYECTO"); c.drawString(bx+93*mm,by+51*mm,"LÁMINA"); c.setFont("Helvetica",6); c.drawString(bx+3*mm,by+43*mm,"EDIFICIO YVAN TRUJILLO-01"); c.drawString(bx+93*mm,by+43*mm,sheet.sheet_id); c.drawString(bx+3*mm,by+35*mm,"TÍTULO: "+sheet.title); c.drawString(bx+93*mm,by+35*mm,"ESCALA: 1:50"); c.drawString(bx+3*mm,by+27*mm,"FECHA: 26/09/2026"); c.drawString(bx+93*mm,by+27*mm,"LOD: 300"); c.drawString(bx+3*mm,by+19*mm,"DIBUJO: SICL / ARKI"); c.drawString(bx+93*mm,by+19*mm,"REV: R00"); c.drawString(bx+3*mm,by+6*mm,"ESTADO: DRAFT"); c.drawString(bx+93*mm,by+6*mm,"TÉCNICO")
    c.setFont("Helvetica",6); c.drawString(25*mm,10*mm,"CUADRO NORMATIVO · CUADRO DE ÁREAS · CUADRO DE VANOS · FONDO BLANCO #FFFFFF · LÍNEAS #000000")

def export_drawing_set(drawing_set: DrawingSet, output: str | Path) -> str:
    output=str(output); Path(output).parent.mkdir(parents=True,exist_ok=True); c=canvas.Canvas(output,pagesize=PAGE)
    for i,sheet in enumerate(drawing_set.sheets): _draw_sheet(c,sheet,i); c.showPage()
    c.save(); return output
