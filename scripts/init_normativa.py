import sqlite3
import json
from pathlib import Path

# Crear directorio de datos
Path("data").mkdir(exist_ok=True)

# Conectar a DB de normativa
conn = sqlite3.connect("data/normativa.db")
cursor = conn.cursor()

# Crear tablas
cursor.execute("""
CREATE TABLE IF NOT EXISTS articulos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    norma TEXT NOT NULL,
    articulo TEXT NOT NULL,
    titulo TEXT,
    contenido TEXT NOT NULL,
    categoria TEXT,
    keywords TEXT
)
""")

# Insertar ejemplos de RNE (Reglamento Nacional de Edificaciones)
rne_samples = [
    ("RNE-A.010", "Artículo 1", "Condiciones Generales", 
     "Todas las edificaciones deben cumplir con las condiciones de seguridad, salubridad y comodidad.",
     "seguridad, salubridad, comodidad", "general"),
    
    ("RNE-A.020", "Artículo 2", "Clasificación de Edificaciones",
     "Las edificaciones se clasifican según su uso: residencial, comercial, industrial, institucional, recreacional.",
     "clasificación, uso, tipología", "clasificacion"),
    
    ("RNE-A.030", "Artículo 3", "Requisitos de Diseño",
     "El diseño arquitectónico debe considerar: iluminación natural, ventilación, accesibilidad universal y seguridad estructural.",
     "diseño, iluminación, ventilación, accesibilidad", "diseno"),
    
    ("RNE-A.060", "Artículo 6", "Disposiciones para Edificaciones de Salud",
     "Los establecimientos de salud deben cumplir: áreas mínimas, circulación diferenciada, zonas limpias y sucias, aislamiento.",
     "hospitales, salud, áreas mínimas, circulación", "salud"),
    
    ("RNE-A.100", "Artículo 10", "Estacionamientos",
     "Todo proyecto debe considerar estacionamientos según el uso: 1 cajón cada 100m² para oficinas, 1 cada 50m² para comercio.",
     "estacionamientos, parqueaderos, áreas mínimas", "estacionamientos"),
    
    ("RNE-A.110", "Artículo 11", "Áreas Libres y Jardines",
     "Se requiere un mínimo del 20% de área libre en lotes urbanos. Jardines deben tener riego automático si superan 100m².",
     "áreas libres, jardines, porcentaje", "areas_libres"),
    
    ("RNE-A.120", "Artículo 12", "Accesibilidad Universal",
     "Todas las edificaciones deben ser accesibles: rampas 1:12, pasillos mínimo 1.20m, puertas 0.90m, ascensores si hay más de 1 piso.",
     "accesibilidad, rampas, discapacidad, universal", "accesibilidad"),
    
    ("RNE-A.130", "Artículo 13", "Requisitos de Seguridad",
     "Las edificaciones deben contar con: salidas de emergencia, señalización, extintores, sistema contra incendios.",
     "seguridad, emergencias, incendios, salidas", "seguridad"),
    
    ("RNE-EM.010", "Artículo EM-1", "Instalaciones Eléctricas",
     "Toda edificación requiere instalación eléctrica con tablero general, circuito independiente para cocina y lavandería, puesta a tierra.",
     "electricidad, instalaciones, tablero", "electrico"),
    
    ("RNE-IS.010", "Artículo IS-1", "Instalaciones Sanitarias",
     "Se requiere: agua potable, desagüe, ventilación de tuberías, tanque séptico si no hay red pública.",
     "sanitarias, agua, desagüe, tuberías", "sanitario"),
]

cursor.executemany("""
INSERT OR REPLACE INTO articulos (norma, articulo, titulo, contenido, keywords, categoria)
VALUES (?, ?, ?, ?, ?, ?)
""", rne_samples)

# Insertar ejemplos de OECE (Oficina de Contrataciones del Estado)
oece_samples = [
    ("OECE-Ley30225", "Ley de Contrataciones", "Artículo 1",
     "Las contrataciones del Estado se rigen por los principios de: eficiencia, transparencia, igualdad de trato, competencia.",
     "contrataciones, principios, transparencia", "licitaciones"),
    
    ("OECE-Ley30225", "Ley de Contrataciones", "Artículo 15",
     "Los procesos de selección pueden ser: Licitación Pública, Concurso Público, Adjudicación Simplificada, Subasta Inversa.",
     "procesos, selección, licitación, concurso", "procesos"),
    
    ("OECE-DS016", "Decreto Supremo", "Artículo 5",
     "Para obras mayores a 10 millones de soles es obligatorio constituir una Junta de Resolución de Disputas (JPRD).",
     "JPRD, disputas, obras, 10 millones", "jprd"),
    
    ("OECE-DS016", "Decreto Supremo", "Artículo 8",
     "El expediente técnico debe contener: memoria descriptiva, estudios básicos, planos, especificaciones técnicas, presupuesto, cronograma.",
     "expediente técnico, documentación, requisitos", "expediente"),
]

cursor.executemany("""
INSERT OR REPLACE INTO articulos (norma, articulo, titulo, contenido, keywords, categoria)
VALUES (?, ?, ?, ?, ?, ?)
""", oece_samples)

conn.commit()
conn.close()

print("✅ Base de datos normativa.db creada con RNE y OECE.")
