"""Generador experimental de reportes ISO/IEC 42001; no es certificación legal."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ISO42001Auditor:
    """Genera reportes basados en logs; sin evidencia devuelve NOT_EVALUATED."""

    def __init__(self, compliance_log_path: Path | None = None):
        if compliance_log_path is None:
            compliance_log_path = Path(__file__).parent.parent.parent.parent / "bridge" / "logs" / "compliance_audit.log"
        self.log_path = Path(compliance_log_path)

    def generate_audit_report(self, project_id: str = "global") -> dict[str, Any]:
        entries: list[dict[str, Any]] = []
        if self.log_path.exists():
            with self.log_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        entries.append(json.loads(line))
        total = len(entries)
        compliant = sum(1 for entry in entries if entry.get("status") == "COMPLIANT")
        rate = compliant / total * 100 if total else None
        status = "NOT_EVALUATED" if total == 0 else ("COMPLIANT" if compliant / total >= 0.95 else "NON_COMPLIANT")
        return {
            "standard": "ISO/IEC 42001",
            "auditDate": datetime.now(timezone.utc).isoformat(),
            "projectId": project_id,
            "summary": {"totalValidations": total, "compliantCount": compliant, "complianceRate": rate},
            "controlsVerified": ["A.5.1 Policies for AI", "A.6.1 Risk assessment and treatment", "A.7.1 AI system impact assessment", "A.8.1 Transparency and explainability"],
            "status": status,
            "recentEntries": entries[-10:] if entries else [],
            "evidenceStatus": "INSUFFICIENT_EVIDENCE" if total == 0 else "EVIDENCE_PRESENT",
        }


__all__ = ["ISO42001Auditor"]
