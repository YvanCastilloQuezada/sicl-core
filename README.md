# SICL Core

> **Primero:** lea [000 — LEER PRIMERO: Continuidad y operación de ARKI en el servidor](000_LEER_PRIMERO_CONTINUIDAD_Y_OPERACION.md). Define Arki-02 como entorno operativo primario y GitHub como espejo de código.

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

## Operación en Arki-02

El runtime objetivo de SICL Core es el servidor físico Arki-02 (Ubuntu). GitHub conserva el espejo versionado del código; no es el entorno de producción. La sincronización servidor↔GitHub debe seguir el protocolo de [000 — Continuidad y operación](000_LEER_PRIMERO_CONTINUIDAD_Y_OPERACION.md): fetch, inspección de SHA, fast-forward cuando sea seguro y bloqueo ante árboles dirty o divergencias. No usar Railway como destino de despliegue.

Para la instalación real, consulte el inventario de servicios, rutas, variables y puertos de Arki-02. No se deben inferir ni inventar unidades systemd ni rutas de producción a partir de esta guía general.

Las pruebas locales se ejecutan en el servidor sobre el checkout que se va a desplegar:

```bash
python -m pytest -ra
python -m compileall -q src api tests
```

Un CI verde en GitHub no sustituye las pruebas locales ni el health check de Core en Arki-02.

## Licencia

Este repositorio se distribuye actualmente como **Proprietary — All rights reserved**. Cualquier cambio a una licencia abierta requiere una decisión explícita del Product Owner.
