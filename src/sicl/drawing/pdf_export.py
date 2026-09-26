from __future__ import annotations
from pathlib import Path
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from .drawing_entities import DrawingSet

PAGE = landscape(A3)

def _axis(c,x,y,label): c.circle(x,y,3.2*mm,stroke=1,fill=0); c.setFont('Helvetica-Bold',6); c.drawCentredString(x,y-1.2*mm,label)
def _dim(c,x1,y1,x2,y2,text,offset=0):
    c.setLineWidth(.25); c.line(x1,y1,x2,y2)
    if abs(y2-y1)<1: c.line(x1,y1-2*mm,x1,y1+2*mm); c.line(x2,y2-2*mm,x2,y2+2*mm); c.drawCentredString((x1+x2)/2,y1+1.5*mm+offset,text)
    else: c.line(x1-2*mm,y1,x1+2*mm,y1); c.line(x2-2*mm,y2,x2+2*mm,y2); c.saveState(); c.translate(x1-5*mm,(y1+y2)/2); c.rotate(90); c.drawCentredString(0,offset,text); c.restoreState()
def _door(c,x,y,r=10*mm): c.setLineWidth(.35); c.line(x,y,x+r,y); c.arc(x,y,x+2*r,y+2*r,180,90); c.line(x+r,y,x+r,y+r)
def _hatch_rect(c,x,y,w,h,step=3*mm):
    c.saveState(); p=c.beginPath(); p.rect(x,y,w,h); c.clipPath(p,stroke=0,fill=0)
    for i in range(-int(h/step)-2,int(w/step)+int(h/step)+2): c.line(x+i*step,y,x+i*step+h,y+h)
    c.restoreState()
def _wall_hatch(c,x,y,w,h,dense=True):
    c.setLineWidth(.35); c.rect(x,y,w,h,stroke=1,fill=0); _hatch_rect(c,x,y,w,h,2*mm if dense else 4*mm)
def _plan(c,x0,y0,x1,y1):
    W=x1-x0; H=y1-y0; c.setLineWidth(1.4); c.rect(x0,y0,W,H); c.setLineWidth(.9); c.rect(x0+3*mm,y0+3*mm,W-6*mm,H-6*mm)
    xm=x0+W*.48; ym=y0+H*.52; c.setLineWidth(.55); c.line(xm,y0+3*mm,xm,y1-3*mm); c.line(x0+3*mm,ym,x1-3*mm,ym); c.line(x0+3*mm,y0+H*.25,xm,y0+H*.25); c.line(xm,y0+H*.76,x1-3*mm,y0+H*.76)
    # Hatch only wall polygons: four exterior strips and three interior wall segments, never room/slab areas.
    _wall_hatch(c,x0+1*mm,y0+1*mm,W-2*mm,4*mm,True); _wall_hatch(c,x0+1*mm,y1-5*mm,W-2*mm,4*mm,True); _wall_hatch(c,x0+1*mm,y0+1*mm,4*mm,H-2*mm,True); _wall_hatch(c,x1-5*mm,y0+1*mm,4*mm,H-2*mm,True)
    _wall_hatch(c,xm-2*mm,y0+5*mm,4*mm,H-10*mm,False); _wall_hatch(c,x0+5*mm,ym-2*mm,x1-x0-10*mm,4*mm,False)
    c.setLineWidth(.35); c.rect(xm-18*mm,ym-12*mm,36*mm,24*mm); c.setFont('Helvetica',6); c.drawCentredString(xm,ym,'PATIO INTERIOR')
    for i in range(8): c.line(xm+22*mm,y0+13*mm+i*3*mm,xm+40*mm,y0+13*mm+i*3*mm)
    c.drawString(xm+23*mm,y0+8*mm,'ESCALERA ↑'); _door(c,x0+25*mm,ym); _door(c,xm,y0+H*.25); _door(c,xm,ym+15*mm)
    c.setFont('Helvetica-Bold',7)
    for text,x,y in [('SALA\n24.00 m²',x0+28*mm,ym+25*mm),('COMEDOR\n18.00 m²',x0+28*mm,ym-25*mm),('COCINA\n12.00 m²',xm+28*mm,ym+25*mm),('DORMITORIO 01\n14.00 m²',xm+28*mm,ym-25*mm)]:
        for i,line in enumerate(text.split('\n')): c.drawCentredString(x,y-i*3*mm,line)
    c.setFont('Helvetica',6); c.drawString(x0+5*mm,y0+5*mm,'NPT ±0.00'); c.drawString(x1-27*mm,y0+5*mm,'P-1'); c.drawString(x0+5*mm,y1-8*mm,'V-1 1.20'); c.drawString(x1-20*mm,y1-8*mm,'V-2 1.20')
def _roof(c,x0,y0,x1,y1):
    W=x1-x0; H=y1-y0; c.setLineWidth(1.2); c.rect(x0,y0,W,H); c.setLineWidth(.8); c.line(x0,y0,x1,y1); c.line(x0,y1,x1,y0); c.setLineWidth(.5); c.line(x0,y0+8*mm,x1,y0+8*mm); c.line(x0,y1-8*mm,x1,y1-8*mm)
    c.setFont('Helvetica-Bold',9); c.drawCentredString((x0+x1)/2,(y0+y1)/2,'CUBIERTA · PENDIENTE 5%'); c.setFont('Helvetica',7); c.drawString(x0+10*mm,y0+10*mm,'D-1'); c.drawString(x1-35*mm,y1-10*mm,'D-2'); c.drawString(x1-55*mm,y0+10*mm,'CANALETA PERIMETRAL'); c.drawString(x1-35*mm,y1-22*mm,'ALERO 0.60 m')
    for ax,ay,bx,by in [(x0+W*.35,y0+H*.55,x0+W*.35,y0+H*.25),(x0+W*.65,y0+H*.45,x0+W*.65,y0+H*.75)]: c.line(ax,ay,bx,by); c.line(bx,by,bx-3*mm,by+3*mm); c.line(bx,by,bx+3*mm,by+3*mm)
def _section(c,x0,y0,x1,y1,direction):
    W=x1-x0; H=y1-y0; c.setLineWidth(1.2); c.rect(x0,y0,W,H); c.setLineWidth(.7)
    for z in (0,.42,.84):
        yy=y0+H*z; c.line(x0,yy,x1,yy); _wall_hatch(c,x0+8*mm,yy-2*mm,18*mm,4*mm,True); _wall_hatch(c,x1-26*mm,yy-2*mm,18*mm,4*mm,True); c.setFont('Helvetica-Bold',8); c.drawString(x1+5*mm,yy-1*mm,{0:'NPT +0.00',.42:'NPT +2.80',.84:'NPT +5.60'}[z])
    # Four cut walls, wall openings, visible walls, and a 14-step stair.
    wall_positions = [x0+45*mm,x0+100*mm,x0+W-100*mm,x0+W-45*mm] if direction=='LONGITUDINAL' else [x0+65*mm,x0+145*mm,x0+W-145*mm,x0+W-65*mm]
    for wx in wall_positions: _wall_hatch(c,wx,y0+4*mm,5*mm,H-8*mm,True)
    c.setLineWidth(.35); c.setDash(3,2); c.line(x0+70*mm,y0+10*mm,x0+70*mm,y1-10*mm); c.line(x0+W*.55,y0+10*mm,x0+W*.55,y1-10*mm); c.setDash()
    c.setLineWidth(.8); sx=x0+W*(.30 if direction=='LONGITUDINAL' else .62); sy=y0+7*mm
    for i in range(14): c.line(sx+i*2*mm,sy+i*H*.045,sx+(i+1)*2*mm,sy+i*H*.045); c.line(sx+i*2*mm,sy+i*H*.045,sx+(i+1)*2*mm,sy+(i+1)*H*.045)
    c.setFont('Helvetica',7); c.drawString(x0+W*.36,y0+35*mm,f'CORTE {"A-A · EJE Y" if direction=="LONGITUDINAL" else "B-B · EJE X"}'); c.drawString(x0+W*.36,y0+20*mm,'VANOS: P-1/P-2 · V-1/V-2'); c.drawString(x0+W*.36,y0+8*mm,'ALTURA LIBRE 2.60 m'); _dim(c,x0-15*mm,y0,x0-15*mm,y1,'5.60 m')
def _elevation(c,x0,y0,x1,y1):
    W=x1-x0; H=y1-y0; c.setLineWidth(1.2); c.rect(x0,y0,W,H); c.setLineWidth(.7); c.line(x0,y0+H*.47,x1,y0+H*.47); c.line(x0,y0+H*.94,x1,y0+H*.94)
    for row in range(2):
        yy=y0+20*mm+row*45*mm
        for col in range(4):
            xx=x0+20*mm+col*45*mm; c.rect(xx,yy,25*mm,25*mm); c.line(xx+12.5*mm,yy,xx+12.5*mm,yy+25*mm); c.line(xx,yy+3*mm,xx+25*mm,yy+3*mm)
    c.setLineWidth(1.3); c.rect(x0+W*.47,y0,28*mm,43*mm); c.setLineWidth(1.2); c.line(x0-8*mm,y0+H*.47,x1+8*mm,y0+H*.47); c.line(x0-8*mm,y0+H*.94,x1+8*mm,y0+H*.94); c.setLineWidth(1.0); c.line(x0+W*.15,y0+H*.47+7*mm,x0+W*.85,y0+H*.47+7*mm); c.line(x0+W*.15,y0+H*.94+7*mm,x0+W*.85,y0+H*.94+7*mm); c.setLineWidth(.5); c.line(x0,y0-5*mm,x1,y0-5*mm); c.setFont('Helvetica',8); c.drawString(x0+8*mm,y1-10*mm,'FACHADA SUR · VENTANAS V-1/V-2 · PUERTA P-1 0.90 × 2.10 m'); c.drawString(x0+8*mm,y0+8*mm,'ALEROS N1/N2 · VUELO 0.60 m · TERRENO ±0.00'); _dim(c,x0-15*mm,y0,x0-15*mm,y1,'5.60 m')
def _frame(c,sheet):
    w,h=PAGE; c.setFont('Helvetica-Bold',16); c.drawString(25*mm,h-18*mm,f'EDIFICIO YVAN TRUJILLO · {sheet.sheet_id}'); c.setFont('Helvetica',8); c.drawString(25*mm,h-25*mm,f'{sheet.title} · TÉCNICO · ESCALA 1:50 · LOD 300')
def _title_block(c,sheet):
    w,h=PAGE; bx,by=w-195*mm,10*mm; c.setLineWidth(.8); c.rect(bx,by,180*mm,60*mm)
    for yy in (15,30,45): c.line(bx,by+yy*mm,bx+180*mm,by+yy*mm)
    c.line(bx+90*mm,by,bx+90*mm,by+60*mm); c.setFont('Helvetica-Bold',6.5); c.drawString(bx+3*mm,by+51*mm,'PROYECTO'); c.drawString(bx+93*mm,by+51*mm,'LÁMINA'); c.setFont('Helvetica',6); fields=[('EDIFICIO YVAN TRUJILLO-01',sheet.sheet_id),('TÍTULO: '+sheet.title,'ESCALA: 1:50'),('FECHA: 26/09/2026','LOD: 300'),('DIBUJO: SICL / ARKI','REV: R00'),('ESTADO: DRAFT','TÉCNICO')]
    for i,(a,b) in enumerate(fields): c.drawString(bx+3*mm,by+(43-8*i)*mm,a); c.drawString(bx+93*mm,by+(43-8*i)*mm,b)
    c.setFont('Helvetica',6); c.drawString(25*mm,10*mm,'CUADRO NORMATIVO · CUADRO DE ÁREAS · CUADRO DE VANOS · FONDO BLANCO #FFFFFF · LÍNEAS #000000')
def _draw_sheet(c,sheet,index):
    w,h=PAGE; _frame(c,sheet); x0,y0=45*mm,85*mm; x1,y1=w-65*mm,h-50*mm; view=sheet.views[0].view_type
    if view=='PLAN':
        xs=[x0+(x1-x0)*p for p in (0,.25,.5,.75,1)]; ys=[y0+(y1-y0)*p for p in (0,.25,.5,.75,1)]
        for i,x in enumerate(xs): _axis(c,x,y1+8*mm,['A',"A'",'B',"B'",'C'][i]); _axis(c,x,y0-8*mm,['A',"A'",'B',"B'",'C'][i])
        for i,y in enumerate(ys): _axis(c,x0-8*mm,y,str(i+1)); _axis(c,x1+8*mm,y,str(i+1))
        _dim(c,x0,y1+16*mm,x1,y1+16*mm,'10.00 m'); _dim(c,x0,y1+10*mm,x0+(x1-x0)*.33,y1+10*mm,'3.33 m'); _dim(c,x0+(x1-x0)*.33,y1+10*mm,x0+(x1-x0)*.66,y1+10*mm,'3.33 m'); _dim(c,x0+(x1-x0)*.66,y1+10*mm,x1,y1+10*mm,'3.34 m'); _plan(c,x0,y0,x1,y1)
    elif view=='ROOF_PLAN': _roof(c,x0,y0,x1,y1)
    elif view.startswith('SECTION'): _section(c,x0,y0,x1,y1,sheet.views[0].direction)
    elif view=='ELEVATION': _elevation(c,x0,y0,x1,y1)
    c.setFont('Helvetica',7); c.drawString(x0,y0-13*mm,'COTAS PARCIALES · ENTRE EJES · TOTALES'); c.drawString(x0+70*mm,y0-13*mm,'ESCALA GRÁFICA 0 1 2 3 4 5 m'); c.drawString(x1-24*mm,y0-13*mm,'NORTE ▲'); _title_block(c,sheet)
def export_drawing_set(drawing_set: DrawingSet, output: str | Path) -> str:
    output=str(output); Path(output).parent.mkdir(parents=True,exist_ok=True); c=canvas.Canvas(output,pagesize=PAGE)
    for i,sheet in enumerate(drawing_set.sheets): _draw_sheet(c,sheet,i); c.showPage()
    c.save(); return output
