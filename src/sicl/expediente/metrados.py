"""
ARKI - Motor de Metrados (LOD 200-300)
Toma la geometría conceptual (geometry2d, geometry3d) y calcula metrados de partidas básicas.
"""

class MetradosEngine:
    def __init__(self, geometry2d, geometry3d):
        self.geo2d = geometry2d or {}
        self.geo3d = geometry3d or {}

    def calcular(self):
        # Extraemos las dimensiones
        footprint = self.geo2d.get("footprintM2", 0)
        width = self.geo2d.get("widthM", 0)
        depth = self.geo2d.get("depthM", 0)
        courtyard = self.geo2d.get("courtyardM2", 0)
        floors = self.geo3d.get("floors", 1)
        height = self.geo3d.get("heightM", 3.0)

        # Reglas de cálculo simplificadas para LOD 200
        area_techada = footprint * floors
        perimetro = 2 * (width + depth)
        muros = perimetro * height * floors  # m2 de muro
        losas = footprint * floors           # m2 de losa
        columnas = (perimetro / 5) * height * floors  # Estimación: 1 columna cada 5m

        # Estimaciones de concreto (ratios típicos peruanos)
        concreto_columnas = columnas * 0.25 * 0.25 * height  # m3
        concreto_losas = losas * 0.20                         # m3 (espesor 20cm)
        acero_estimado = (concreto_columnas + concreto_losas) * 100 # kg (ratio 100kg/m3)

        return {
            "project_summary": {
                "area_techada_m2": round(area_techada, 2),
                "huella_m2": round(footprint, 2),
                "patio_m2": round(courtyard, 2),
                "pisos": floors,
                "altura_m": height
            },
            "partidas": {
                "ESTRUCTURAS": {
                    "concreto_columnas_m3": round(concreto_columnas, 2),
                    "concreto_losas_m3": round(concreto_losas, 2),
                    "acero_kg": round(acero_estimado, 2),
                    "encofrado_m2": round(columnas + losas, 2)
                },
                "ARQUITECTURA": {
                    "muros_m2": round(muros, 2),
                    "pisos_m2": round(area_techada, 2),
                    "cielos_rasos_m2": round(area_techada, 2)
                }
            },
            "unit_prices_reference": {
                "concreto_m3": 450.00,
                "acero_kg": 5.50,
                "muro_m2": 120.00,
                "piso_m2": 65.00
            }
        }
