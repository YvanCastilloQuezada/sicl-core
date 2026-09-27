"""Tests para el generador de reportes ISO/IEC 42001."""
import json
import tempfile
from pathlib import Path

import pytest

from sicl.compliance.iso_42001 import ISO42001Auditor


def test_iso_42001_empty_log_report():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as handle:
        temp_path = Path(handle.name)
    try:
        report = ISO42001Auditor(temp_path).generate_audit_report("test-project")
        assert report["standard"] == "ISO/IEC 42001"
        assert report["summary"]["totalValidations"] == 0
        assert report["summary"]["complianceRate"] is None
        assert report["status"] == "NOT_EVALUATED"
        assert report["evidenceStatus"] == "INSUFFICIENT_EVIDENCE"
    finally:
        temp_path.unlink(missing_ok=True)


def test_iso_42001_compliant_log_report():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as handle:
        handle.write(json.dumps({"status": "COMPLIANT", "ruleId": "RULE_41"}) + "\n")
        handle.write(json.dumps({"status": "COMPLIANT", "ruleId": "RULE_42"}) + "\n")
        handle.write(json.dumps({"status": "NON_COMPLIANT", "ruleId": "RULE_43"}) + "\n")
        temp_path = Path(handle.name)
    try:
        report = ISO42001Auditor(temp_path).generate_audit_report("test-project")
        assert report["summary"]["totalValidations"] == 3
        assert report["summary"]["compliantCount"] == 2
        assert report["summary"]["complianceRate"] == pytest.approx(66.66, rel=1e-2)
        assert report["status"] == "NON_COMPLIANT"
    finally:
        temp_path.unlink(missing_ok=True)
