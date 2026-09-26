from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from pathlib import Path

@dataclass(frozen=True)
class DrawingRule:
    key: str
    value: object
    source: str

@dataclass(frozen=True)
class DrawingRuleSet:
    rule_set_id: str
    standard: str
    scale: str
    lod: int
    source: str
    rules: tuple[DrawingRule, ...]
    def to_dict(self):
        return {"rule_set_id": self.rule_set_id, "standard": self.standard, "scale": self.scale, "lod": self.lod, "source": self.source, "rules": [asdict(rule) for rule in self.rules]}

def load_rule_set(path: str | Path, scale: str = "1:50", lod: int = 300) -> DrawingRuleSet:
    source = str(path); data = json.loads(Path(path).read_text())
    if not data.get("standard") or not data.get("rules"): raise ValueError("rule set requires standard and rules source")
    rules = tuple(DrawingRule(k, v, source) for k, v in data["rules"].items())
    return DrawingRuleSet(data.get("id", Path(path).stem), data["standard"], scale, lod, source, rules)

def validate_rule_set(rule_set: DrawingRuleSet) -> list[str]:
    required = {"line_weights", "hatches", "scales", "colors"}; keys = {rule.key for rule in rule_set.rules}
    return sorted(required - keys)
