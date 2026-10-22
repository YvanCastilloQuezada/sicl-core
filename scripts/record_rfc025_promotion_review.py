from __future__ import annotations

import json
from pathlib import Path

fixture = Path(__file__).parents[1] / "data" / "regulatory" / "rne_a010_sample.json"
payload = json.loads(fixture.read_text(encoding="utf-8"))
payload["promotion_review"] = {
    "review_id": "PROMOTION-REVIEW-RFC025-2026-09-16",
    "reviewed_at": "2026-09-16T23:13:00Z",
    "reviewer": "Manus AI — evidence pre-review",
    "status": "BLOCKED",
    "source_availability": "ALL_SIX_SOURCES_HTTP_200",
    "decision": "NO_AUTOMATIC_PROMOTION",
    "reason": "HTTP availability does not prove legal vigency; E.030 and IS.010 have official modification notices after the fixture versions, while current status evidence is incomplete for the full five-norm set.",
    "blocked_regulations": ["A.010", "E.030", "E.060", "IS.010", "EM.010"],
    "follow_up_sources": [
        "https://www.gob.pe/institucion/vivienda/normas-legales/8081915-183-2026-vivienda",
        "https://www.gob.pe/institucion/vivienda/normas-legales/6500515-055-2025-vivienda",
        "https://www.gob.pe/institucion/vivienda/normas-legales/6667128-107-2025-vivienda"
    ]
}
fixture.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
