"""
ARKI - Motor de Análisis Físico y Normativo (Básico)
Calcula asoleamiento, incendios, viento y estructura usando fórmulas simplificadas.
"""
import math

class BIMAnalyzer:
    def __init__(self, geometry2d, geometry3d, location_lat=-8.11):
        self.geo2d = geometry2d
        self.geo3d = geometry3d
        self.lat = location_lat # Trujillo por defecto
        self.floors = geometry3d.get("floors", 1)
        self.height = geometry3d.get("heightM", 3.0) * self.floors
        self.area = geometry2d.get("footprintM2", 0)

    def analyze_solar(self):
        """Estimación básica de asoleamiento."""
        # Horas de sol pico estimadas según latitud (simplificado)
        peak_sun_hours = 5.5 
        # Ganancia solar aproximada (kWh/m2/año) - depende de la ventana
        solar_gain = peak_sun_hours * 365 * 0.4 # Factor de sombreamiento 0.4
        return {
            "peak_sun_hours": peak_sun_hours,
            "estimated_solar_gain_kwh_m2": round(solar_gain, 2),
            "recommendation": "Usar aleros en fachada Norte para control solar." if solar_gain > 800 else "Ganancia solar moderada."
        }

    def analyze_fire(self):
        """Evalúa rutas de evacuación según RNE A.130."""
        # Distancia máxima de recorrido (RNE A.130: 45m para riesgo moderado)
        max_travel_distance = 45.0
        # Estimación de ruta crítica basada en el área (simplificado)
        estimated_travel = math.sqrt(self.area) / 2
        
        is_safe = estimated_travel <= max_travel_distance
        return {
            "max_allowed_distance_m": max_travel_distance,
            "estimated_travel_distance_m": round(estimated_travel, 2),
            "status": "CUMPLE" if is_safe else "NO CUMPLE",
            "recommendation": "Añadir escalera de emergencia." if not is_safe else "Ruta de evacuación OK."
        }

    def analyze_wind(self):
        """Carga de viento según RNE E.020."""
        # Velocidad básica de viento en Trujillo (aprox 75 km/h)
        v_basic = 75.0 # km/h
        # Presión dinámica: q = 0.005 * V^2 (en kg/m2)
        q = 0.005 * (v_basic ** 2)
        # Factor de forma (simplificado para edificio rectangular)
        c_f = 1.3 
        pressure = q * c_f
        
        return {
            "wind_speed_kmh": v_basic,
            "dynamic_pressure_kg_m2": round(q, 2),
            "design_pressure_kg_m2": round(pressure, 2),
            "recommendation": "Verificar anclajes de fachada." if pressure > 100 else "Carga de viento moderada."
        }

    def analyze_structural(self):
        """Predimensionamiento básico y peso sísmico (RNE E.030/E.060)."""
        # Peso sísmico estimado: 1 ton/m2 por piso (concreto + acabados)
        seismic_weight = self.area * self.floors * 1.0 # toneladas
        
        # Predimensionamiento de columna central (Área tributaria simplificada)
        # P = 1.5 * (Área tributaria * pisos * 1 ton/m2)
        column_load = 1.5 * ((self.area / 10) * self.floors * 1.0) # 10 columnas asumidas
        # Área de acero requerida (P / (0.3 * f'c))
        column_area_cm2 = (column_load * 1000) / (0.3 * 210) 
        
        return {
            "estimated_seismic_weight_ton": round(seismic_weight, 2),
            "estimated_column_load_ton": round(column_load, 2),
            "required_column_area_cm2": round(column_area_cm2, 2),
            "recommendation": "Usar columnas de 30x30 cm mínimo." if column_area_cm2 < 900 else "Usar columnas de 40x40 cm o placas."
        }
