#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import ifcopenshell
import ifcopenshell.api

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/EDIFICIO-YVAN-TRUJILLO-01.ifc')

def run(model, usecase, **kwargs):
    return ifcopenshell.api.run(usecase, model, **kwargs)

def placement(x=0.0, y=0.0, z=0.0, angle=0.0):
    c, s = np.cos(angle), np.sin(angle)
    m = np.eye(4); m[:3,:3] = [[c,-s,0],[s,c,0],[0,0,1]]; m[:3,3] = [x,y,z]
    return m

def make_model():
    model = run(None, 'project.create_file', version='IFC4')
    project = run(model, 'root.create_entity', ifc_class='IfcProject', name='EDIFICIO-YVAN-TRUJILLO-01')
    run(model, 'unit.assign_unit', length={'is_metric': True, 'raw': 'METERS'}, area={'is_metric': True, 'raw': 'SQUARE_METERS'}, volume={'is_metric': True, 'raw': 'CUBIC_METERS'})
    model_context = run(model, 'context.add_context', context_type='Model')
    body = run(model, 'context.add_context', context_type='Model', context_identifier='Body', target_view='MODEL_VIEW', parent=model_context)
    plan = run(model, 'context.add_context', context_type='Plan', context_identifier='Annotation', target_view='PLAN_VIEW', parent=model_context)
    site = run(model, 'root.create_entity', ifc_class='IfcSite', name='SITE')
    building = run(model, 'root.create_entity', ifc_class='IfcBuilding', name='BUILDING')
    n1 = run(model, 'root.create_entity', ifc_class='IfcBuildingStorey', name='N1', predefined_type='ELEMENT',)
    n2 = run(model, 'root.create_entity', ifc_class='IfcBuildingStorey', name='N2', predefined_type='ELEMENT')
    roof = run(model, 'root.create_entity', ifc_class='IfcBuildingStorey', name='TECHO', predefined_type='ELEMENT')
    n1.Elevation = 0.0; n2.Elevation = 2.8; roof.Elevation = 5.6
    run(model, 'aggregate.assign_object', products=[site], relating_object=project)
    run(model, 'aggregate.assign_object', products=[building], relating_object=site)
    run(model, 'aggregate.assign_object', products=[n1,n2,roof], relating_object=building)
    stores = [(n1,0.0),(n2,2.8)]
    # 4 exterior and 3 interior walls per level, each with real 2-point geometry.
    wall_specs = [
        ('EXT-S', (0,0),(10,0),0.20), ('EXT-E',(10,0),(10,10),0.20), ('EXT-N',(10,10),(0,10),0.20), ('EXT-W',(0,10),(0,0),0.20),
        ('INT-M',(5,0.2),(5,9.8),0.15), ('INT-C',(0.2,5),(9.8,5),0.15), ('INT-P',(5.0,5.0),(8.0,5.0),0.15)]
    walls=[]
    for storey,z in stores:
        for name,p1,p2,thickness in wall_specs:
            wall = run(model,'root.create_entity',ifc_class='IfcWall',name=f'{name}-{storey.Name}',predefined_type='PARTITIONING' if thickness<.2 else 'SOLIDWALL')
            rep = run(model,'geometry.create_2pt_wall',element=wall,context=body,p1=p1,p2=p2,elevation=z,height=2.6,thickness=thickness,is_si=True)
            run(model,'geometry.assign_representation',product=wall,representation=rep)
            wall.Description = 'MATERIAL=CONCRETE' if thickness>=.2 else 'MATERIAL=MASONRY'
            run(model,'spatial.assign_container',products=[wall],relating_structure=storey); walls.append(wall)
    # 3 slabs: floor, intermediate, roof with actual footprint geometry.
    slab_specs=[('SLAB-N1',-0.2,n1),('SLAB-N2',2.6,n2),('SLAB-ROOF',5.4,roof)]
    slabs=[]
    for name,z,storey in slab_specs:
        slab=run(model,'root.create_entity',ifc_class='IfcSlab',name=name,predefined_type='FLOOR')
        rep=run(model,'geometry.add_slab_representation',context=body,depth=.2,polyline=[(0,0),(10,0),(10,10),(0,10),(0,0)])
        run(model,'geometry.assign_representation',product=slab,representation=rep)
        run(model,'geometry.edit_object_placement',product=slab,matrix=placement(0,0,z))
        run(model,'spatial.assign_container',products=[slab],relating_structure=storey); slabs.append(slab)
    # Doors + opening hosts and windows with actual dimensions and placement.
    doors=[]
    for i,(storey,z,x,y) in enumerate([(n1,0,4.55,0),(n1,0,5,4.8),(n2,2.8,4.55,0),(n2,2.8,5,4.8)],1):
        opening=run(model,'root.create_entity',ifc_class='IfcOpeningElement',name=f'OPENING-P-{i}')
        run(model,'geometry.edit_object_placement',product=opening,matrix=placement(x,y,z))
        run(model,'spatial.assign_container',products=[opening],relating_structure=storey)
        door=run(model,'root.create_entity',ifc_class='IfcDoor',name=f'P-{i}',predefined_type='DOOR')
        door.OverallWidth=.90; door.OverallHeight=2.10
        rep=run(model,'geometry.add_door_representation',context=body,overall_width=.90,overall_height=2.10,operation_type='SINGLE_SWING_LEFT')
        run(model,'geometry.assign_representation',product=door,representation=rep)
        run(model,'geometry.edit_object_placement',product=door,matrix=placement(x,y,z))
        run(model,'spatial.assign_container',products=[door],relating_structure=storey); doors.append(door)
        run(model,'feature.add_feature',feature=opening,element=walls[(i-1)%len(walls)])
        run(model,'feature.add_filling',opening=opening,element=door)
    windows=[]
    window_positions=[(n1,0,.3,3),(n1,0,9.7,3),(n1,0,3,9.7),(n2,2.8,.3,3),(n2,2.8,9.7,3),(n2,2.8,3,9.7)]
    for i,(storey,z,x,y) in enumerate(window_positions,1):
        opening=run(model,'root.create_entity',ifc_class='IfcOpeningElement',name=f'OPENING-V-{i}')
        run(model,'geometry.edit_object_placement',product=opening,matrix=placement(x,y,z+.9))
        run(model,'spatial.assign_container',products=[opening],relating_structure=storey)
        win=run(model,'root.create_entity',ifc_class='IfcWindow',name=f'V-{i}',predefined_type='WINDOW')
        win.OverallWidth=1.20; win.OverallHeight=1.20
        rep=run(model,'geometry.add_window_representation',context=body,overall_width=1.20,overall_height=1.20)
        run(model,'geometry.assign_representation',product=win,representation=rep)
        run(model,'geometry.edit_object_placement',product=win,matrix=placement(x,y,z+.9))
        run(model,'spatial.assign_container',products=[win],relating_structure=storey); windows.append(win)
        run(model,'feature.add_feature',feature=opening,element=walls[(i+2)%len(walls)])
        run(model,'feature.add_filling',opening=opening,element=win)
    # Spaces with real footprint solids and quantities.
    for name,longname,x,y,w,h,storey in [('Sala','Sala principal',.4,.4,4.2,4.2,n1),('Cocina','Cocina y comedor',5.2,.4,4.4,4.2,n1),('Dormitorio','Dormitorio principal',.4,5.2,4.2,4.4,n2),('Patio','Patio interior descubierto',5.2,5.2,4.4,4.4,n2)]:
        space=run(model,'root.create_entity',ifc_class='IfcSpace',name=name); space.LongName=longname; space.Description=f'AREA={w*h:.2f} m2'
        rep=run(model,'geometry.add_slab_representation',context=body,depth=.1,polyline=[(0,0),(w,0),(w,h),(0,h),(0,0)])
        run(model,'geometry.assign_representation',product=space,representation=rep); run(model,'geometry.edit_object_placement',product=space,matrix=placement(x,y,storey.Elevation))
    # Stair with a real solid footprint between N1 and N2.
    stair=run(model,'root.create_entity',ifc_class='IfcStair',name='ESC-1',predefined_type='STRAIGHT_RUN'); stair.Description='14 peldaños; ancho 1.00 m; conecta N1-N2'
    rep=run(model,'geometry.add_slab_representation',context=body,depth=2.8,polyline=[(0,0),(1,0),(1,1),(0,1),(0,0)]); run(model,'geometry.assign_representation',product=stair,representation=rep); run(model,'geometry.edit_object_placement',product=stair,matrix=placement(4,4,0)); run(model,'spatial.assign_container',products=[stair],relating_structure=n1)
    # Grid with 7 axes and actual curves.
    grid=run(model,'root.create_entity',ifc_class='IfcGrid',name='GRID-01'); run(model,'spatial.assign_container',products=[grid],relating_structure=n1)
    for tag,axis_type,offset in [('1','UAxes',0),('2','UAxes',3.33),('3','UAxes',6.66),('4','UAxes',10),('A','VAxes',0),('B','VAxes',3.33),('C','VAxes',6.66)]:
        axis=run(model,'grid.create_grid_axis',grid=grid,axis_tag=tag,same_sense=True,uvw_axes=axis_type)
        if axis_type=='UAxes': run(model,'geometry.add_axis_representation',context=plan,axis=((offset,0),(offset,10)))
        else: run(model,'geometry.add_axis_representation',context=plan,axis=((0,offset),(10,offset)))
    return model

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    model=make_model(); model.write(str(OUT)); print(OUT)
if __name__=='__main__': main()
