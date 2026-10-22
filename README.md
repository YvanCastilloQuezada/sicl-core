# SICL Core

SICL (Spatial Intelligence Command Language) es una arquitectura de decisión espacial que conserva la separación entre evidencia, análisis y autoridad humana. El Core es la fuente de verdad del dominio: registra proyectos, hechos, supuestos, objetivos, restricciones, alternativas, evaluaciones, recomendaciones y decisiones mediante eventos trazables.

## Estado actual

**Línea:** SICL Core v1.2 feature set, con API REST FastAPI y persistencia SQLite.

**Estado de verificación:** suite Core/API aprobada localmente; el despliegue remoto y el E2E navegador–API dependen de una URL real del servicio y de `VITE_API_URL` en el frontend.

La recomendación analítica nunca se convierte automáticamente en decisión. La decisión requiere actor y autoridad humana explícitos.

## Estructura

```text
src/sicl/       Dominio, CLI, persistencia y exportaciones
api/             Adaptador REST FastAPI
 tests/          Pruebas del dominio y de la API
docs/            Contratos, alcance y configuración
exports/         Salidas generadas localmente; ignoradas por Git
```

## Requisitos

- Python 3.11 o superior.
- `pip` y un entorno virtual.
- SQLite, incluido en Python.

## Instalación local

```bash
cd sicl-core-v1.0
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[test,api]"
```

## Ejecutar la CLI

```bash
sicl
```

La CLI admite comandos como `/PROJECT CREATE`, `/FACT SET`, `/ASSUMPTION SET`, `/OBJECTIVE SET`, `/CONSTRAINT SET`, `/ALTERNATIVE CREATE`, `/EVALUATE`, `/COMPARE`, `/RECOMMEND`, `/DECISION RECORD` y exportaciones.

## Ejecutar la API

```bash
PYTHONPATH=src uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Verificación:

```bash
curl http://127.0.0.1:8000/health
```

Rutas principales:

| Método | Ruta | Función |
|---|---|---|
| GET | `/health` | Salud del servicio |
| GET | `/projects` | Listar proyectos |
| POST | `/projects` | Crear proyecto |
| GET | `/projects/{project_id}` | Recuperar snapshot |
| PUT | `/projects/{project_id}` | Cambiar etapa |
| POST | `/commands` | Ejecutar comando SICL |

## Pruebas

```bash
python -m pytest -ra
python -m compileall -q src api tests
```

La integración CI instala `.[test,api]` y ejecuta la suite completa. Los datos locales, secretos, bases SQLite y exportaciones no deben subirse al repositorio.

## CORS y frontend

En despliegue, configure únicamente los orígenes conocidos:

```bash
export SICL_CORS_ORIGINS=https://<frontend-host>
```

El frontend utiliza `VITE_API_URL` para apuntar a este servicio. Nunca coloque tokens de servicio en código cliente.

## Despliegue Railway

El servicio incluye `Procfile`, `requirements.txt`, `runtime.txt` y `.env.example`. Consulte [`docs/RAILWAY_DEPLOYMENT.md`](docs/RAILWAY_DEPLOYMENT.md) para conectar el repositorio, generar el dominio público, configurar CORS, montar un volumen persistente y verificar el E2E. La ruta canónica de SQLite en Railway es `SICL_DB_PATH`; `DATABASE_URL=./sicl.db` también se acepta como ruta local compatible.

Para el procedimiento actualizado de producción consulte [`docs/PRODUCTION_CORE_DEPLOYMENT_MANUAL.md`](docs/PRODUCTION_CORE_DEPLOYMENT_MANUAL.md). La suite E2E del Copiloto y SICL está en `tests/test_e2e_ollama_sicl.py` y se ejecuta con:

```bash
PYTHONPATH=.:src pytest -q tests/test_e2e_ollama_sicl.py -ra
```

## Licencia

Este repositorio se distribuye actualmente como **Proprietary — All rights reserved**. Cualquier cambio a una licencia abierta requiere una decisión explícita del Product Owner.
