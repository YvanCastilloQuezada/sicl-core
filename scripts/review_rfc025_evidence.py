from __future__ import annotations

import json
from pathlib import Path

from sicl.regulatory_corpus import evidence_traceability_report, load_corpus_fixture

payload = load_corpus_fixture(Path(__file__).parents[1] / "data" / "regulatory" / "rne_a010_sample.json")
print(json.dumps(evidence_traceability_report(payload), ensure_ascii=False, indent=2))
