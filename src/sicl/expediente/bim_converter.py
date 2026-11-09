"""
ARKI - Motor de Conversión a IFC (Scan-to-BIM)
Toma geometría 2D (extraída de PDF o generada) y la extruye a un modelo IFC 3D.
"""
import ifcopenshell
import ifcopenshell.api
import uuid

class BIMConverter:
    def __init__(self):
        self.model = ifcopenshell.api.run("project.create_file", version="IFC4X3")
        self.project = ifcopenshell.api.run("root.create_entity", self.model, ifc_class="IfcProject", name="ARKI_Converted_Project")
        
        # Configurar unidades (metros)
        ifcopenshell.api.run("unit.assign_unit", self.model, length={"is_metric": True, "raw": "METERS"})
        
        # Crear contexto geométrico
        self.context = ifcopenshell.api.run("context.add_context", self.model, context_type="Model")
        self.body = ifcopenshell.api.run("context.add_context", self.model, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=self.context)
        
        # Crear un sitio
        self.site = ifcopenshell.api.run("root.create_entity", self.model, ifc_class="IfcSite", name="Terreno")
        ifcopenshell.api.run("aggregate.assign_object", self.model, relating_object=self.project, product=self.site)
        
        # Crear un edificio
        self.building = ifcopenshell.api.run("root.create_entity", self.model, ifc_class="IfcBuilding", name="Edificio Convertido")
        ifcopenshell.api.run("aggregate.assign_object", self.model, relating_object=self.site, product=self.building)
        
        # Crear un piso
        self.storey = ifcopenshell.api.run("root.create_entity", self.model, ifc_class="IfcBuildingStorey", name="Nivel 1")
        ifcopenshell.api.run("aggregate.assign_object", self.model, relating_object=self.building, product=self.storey)

    def create_wall_from_2d_line(self, start_pt, end_pt, height=3.0, thickness=0.20):
        """Crea un muro IFC extruyendo una línea 2D."""
        # 1. Crear el muro
        wall = ifcopenshell.api.run("root.create_entity", self.model, ifc_class="IfcWall", name=f"Muro_{uuid.uuid4().hex[:4]}")
        
        # 2. Crear la representación geométrica (Extrusión)
        # En un caso real, usaríamos shapely o trimesh para crear el sólido
        # Aquí usamos la API de ifcopenshell para crear un muro simple basado en una línea
        
        import ifcopenshell.util.element
        import ifcopenshell.util.shape_builder
        
        builder = ifcopenshell.util.shape_builder.ShapeBuilder(self.model)
        
        # Vector director de la línea
        import math
        dx = end_pt[0] - start_pt[0]
        dy = end_pt[1] - start_pt[1]
        length = math.sqrt(dx**2 + dy**2)
        angle = math.atan2(dy, dx)
        
        # Crear el perfil rectangular del muro (largo x espesor)
        profile = builder.rectangle(size=(length, thickness))
        
        # Extruir el perfil en altura
        extrusion = builder.extrude(profile, magnitude=height)
        
        # Asignar representación
        representation = builder.get_representation(self.body, [extrusion])
        ifcopenshell.api.run("geometry.assign_representation", self.model, product=wall, representation=representation)
        
        # Posicionar el muro en el plano 2D
        matrix = builder.translate([start_pt[0], start_pt[1], 0])
        matrix = matrix @ builder.rotate_2d(angle)
        ifcopenshell.api.run("geometry.edit_object_placement", self.model, product=wall, matrix=matrix)
        
        # Asignar al piso
        ifcopenshell.api.run("spatial.assign_container", self.model, relating_structure=self.storey, product=wall)
        
        return wall

    def export_ifc(self, filepath):
        self.model.write(filepath)
        return filepath
