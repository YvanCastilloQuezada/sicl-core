from __future__ import annotations

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.commands import router as commands_router
from api.routes.projects import router as projects_router
from api.routes.v1 import router as v1_router
from api.routes.gis_copilot import router as gis_copilot_router


def create_app() -> FastAPI:
    app = FastAPI(title="SICL Core API", version="1.0.0")
    origins = [origin.strip() for origin in os.getenv("SICL_CORS_ORIGINS", "*").split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(projects_router)
    app.include_router(commands_router)
    app.include_router(v1_router)
    app.include_router(gis_copilot_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "sicl-core-api"}

    return app


app = create_app()
