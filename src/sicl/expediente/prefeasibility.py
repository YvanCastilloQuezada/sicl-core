"""
ARKI - Motor de Pre-factibilidad (Normativa Invierte.pe - Perú)
Clasifica proyectos según UIT y evalúa viabilidad inicial.
"""
from enum import Enum

class DocumentType(Enum):
    FICHA_SIMPLIFICADA = "FICHA_TECNICA_SIMPLIFICADA"
    FICHA_ESTANDAR = "FICHA_TECNICA_ESTANDAR"
    PERFIL = "ESTUDIO_PREINVERSION_PERFIL"

class PrefeasibilityEngine:
    def __init__(self, amount_uit: float, sector: str):
        self.amount_uit = amount_uit
        self.sector = sector.lower()
        # Valor de la UIT en Perú (referencial 2026, ajustable)
        self.uit_value_pen = 5350.00 

    def classify(self):
        """Determina el tipo de documento técnico según el monto en UIT."""
        if self.amount_uit <= 750:
            doc = DocumentType.FICHA_SIMPLIFICADA
            desc = "Proyecto menor. Ficha Técnica Simplificada."
        elif self.amount_uit <= 15000:
            doc = DocumentType.FICHA_ESTANDAR
            desc = "Proyecto estándar. Ficha Técnica Estándar."
        else:
            doc = DocumentType.PERFIL
            desc = "Proyecto de alta complejidad. Estudio de Preinversión a Nivel de Perfil."

        return {
            "monto_uit": self.amount_uit,
            "monto_pen": self.amount_uit * self.uit_value_pen,
            "documento_requerido": doc.value,
            "descripcion": desc
        }

    def evaluate_viability(self, has_brecha: bool, is_fraccionado: bool, has_metodologia: bool):
        """Semáforo de viabilidad según criterios de Invierte.pe."""
        issues = []
        if not has_brecha: issues.append("No cierra brecha prioritaria.")
        if is_fraccionado: issues.append("Posible fraccionamiento detectado (evade tamaño).")
        if not has_metodologia: issues.append("Falta metodología aprobada por el sector.")

        status = "VIABLE" if not issues else "NO_VIABLE"
        return {
            "status": status,
            "issues": issues,
            "recomendacion": "Puede proceder a la fase de Formulación." if status == "VIABLE" else "Revisar los puntos críticos antes de formular."
        }

    def generate_ficha_structure(self, doc_type: DocumentType):
        """Genera el esqueleto JSON de la ficha técnica."""
        base = {
            "1. IDENTIFICACION": {"nombre_proyecto": "", "unidad_formuladora": "", "sector": self.sector},
            "2. DIAGNOSTICO": {"problema_central": "", "brechas": []},
            "3. FORMULACION": {"objetivos": [], "alternativas": []},
            "4. EVALUACION": {"costos": {}, "beneficios": {}}
        }
        if doc_type == DocumentType.FICHA_ESTANDAR:
            base["5. SOSTENIBILIDAD"] = {"plan_mantenimiento": ""}
        return base
