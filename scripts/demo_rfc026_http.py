from __future__ import annotations

import json
import os
from fastapi.testclient import TestClient

from api.main import create_app
from api.deps import get_repository
from sicl.domain import RegulationStatus, SourceType, SpatialScope, Regulation


class DemoRepository:
    def list_regulations(self):
        return [Regulation(
            regulation_id="RNE-E030-DEMO",
            jurisdiction="PE",
            authority="MVCS",
            code="E.030",
            title="Diseño Sismorresistente",
            version="RM-043-2019-VIVIENDA",
            publication_date=None,
            effective_date=None,
            status=RegulationStatus.NO_VERIFICADA,
            source_url="https://www.gob.pe/institucion/vivienda/informes-publicaciones/2309793-reglamento-nacional-de-edificaciones-rne",
            source_type=SourceType.OFFICIAL,
            evidence_hash=None,
            scope_applicable=[SpatialScope.EDIFICACION, SpatialScope.SISTEMA],
            parent_regulation_id=None,
            summary="Demo only; human review required.",
        )]


def main() -> None:
    headers = {"Authorization": f"Bearer {os.getenv('SICL_CORE_SERVICE_TOKEN', '')}"}
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: DemoRepository()
    client = TestClient(app)
    payload = {
        "spatial_scope": "distrito_ciudad",
        "typology": "vivienda",
        "jurisdiction": "PE",
        "objectives": ["confort", "privacidad", "legibilidad urbana"],
        "problem_terms": ["publico", "privado", "barrio"],
        "requested_operation": "STRATEGY_FORMULATION",
        "facts": ["ubicación: Trujillo, Peru"],
        "assumptions": ["se requiere transición gradual entre calle y vivienda"],
        "preferences": ["priorizar confort y privacidad"],
    }
    response = client.post("/v1/design-knowledge/query", headers=headers, json=payload)
    print(json.dumps({"http_status": response.status_code, "response": response.json()}, ensure_ascii=False, indent=2))
    response.raise_for_status()


if __name__ == "__main__":
    main()
