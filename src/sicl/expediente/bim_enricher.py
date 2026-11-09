"""
ARKI - Motor de Enriquecimiento BIM (IFC 4.3)
Toma un IFC base (convertido de PDF) y lo completa con:
- Propiedades (Property Sets)
- Materiales
- Clasificación Uniclass/OmniClass
- Sistemas MEP
"""
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element

class BIMEnricher:
    def __init__(self, ifc_path):
        self.model = ifcopenshell.open(ifc_path)
        schema = self.model.schema
        print(f"   [BIM Enricher] Cargando modelo con esquema: {schema}")
        self.project = self.model.by_type("IfcProject")[0]

    def enrich_walls(self, material_name="Concreto Armado f'c=210 kg/cm2", fire_rating="2h", acoustic_rating="45 dB"):
        """Enriquece todos los muros con materiales y propiedades."""
        walls = self.model.by_type("IfcWall")
        print(f"Enriqueciendo {len(walls)} muros...")

        # 1. Crear el material si no existe
        material = ifcopenshell.api.run("material.add_material", self.model, name=material_name)
        
        for wall in walls:
            # 2. Asignar material al muro
            ifcopenshell.api.run("material.assign_material", self.model, products=[wall], material=material)
            
            # 3. Crear Property Set (Pset_WallCommon)
            pset = ifcopenshell.api.run("pset.add_pset", self.model, product=wall, name="Pset_WallCommon")
            ifcopenshell.api.run("pset.edit_pset", self.model, pset=pset, properties={
                "Reference": "Muro estructural",
                "LoadBearing": True,
                "IsExternal": True,
                "FireRating": fire_rating,
                "AcousticRating": acoustic_rating,
                "ThermalTransmittance": 1.5  # W/m2K
            })

            # 4. Clasificación (Uniclass)
            classification = ifcopenshell.api.run("classification.add_classification", self.model, classification="Uniclass")
            ifcopenshell.api.run("classification.add_reference", self.model, products=[wall], classification=classification, identification="Ss_25_10_30", name="Wall systems")

    def enrich_windows(self):
        """Añade propiedades a las ventanas (vidrio, transmitancia)."""
        windows = self.model.by_type("IfcWindow")
        print(f"Enriqueciendo {len(windows)} ventanas...")
        for window in windows:
            pset = ifcopenshell.api.run("pset.add_pset", self.model, product=window, name="Pset_WindowCommon")
            ifcopenshell.api.run("pset.edit_pset", self.model, pset=pset, properties={
                "Reference": "Ventana de aluminio con vidrio templado",
                "IsExternal": True,
                "ThermalTransmittance": 5.8, # W/m2K (vidrio simple)
                "GlazingAreaFraction": 0.85
            })

    def export(self, output_path):
        self.model.write(output_path)
        print(f"✅ Modelo enriquecido exportado: {output_path}")
