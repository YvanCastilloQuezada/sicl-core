from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.commands import router as commands_router
from api.routes.projects import router as projects_router


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

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "sicl-core-api"}

    return app


app = create_app()
