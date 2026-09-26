from __future__ import annotations
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import Any

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

    def get(self, key: str, default: Any = None) -> Any:
        """Read a dotted rule path, e.g. ``hatches.concrete.pattern``."""
        current: Any = {rule.key: rule.value for rule in self.rules}
        for part in key.split('.'):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

def load_rule_set(path: str | Path, scale: str = "1:50", lod: int = 300) -> DrawingRuleSet:
    source = str(path); data = json.loads(Path(path).read_text())
    if not data.get("standard") or not data.get("rules"):
        raise ValueError("rule set requires standard and rules source")
    rules = tuple(DrawingRule(k, v, source) for k, v in data["rules"].items())
    return DrawingRuleSet(data.get("id", Path(path).stem), data["standard"], scale, lod, source, rules)

def validate_rule_set(rule_set: DrawingRuleSet) -> list[str]:
    required = {"line_weights", "hatches", "scales", "colors", "symbols", "dimensions", "levels"}
    keys = {rule.key for rule in rule_set.rules}
    missing = set(required - keys)
    if not isinstance(rule_set.get('line_weights'), dict): missing.add('line_weights.mapping')
    for material in ('concrete', 'masonry', 'partition'):
        if rule_set.get(f'hatches.{material}.pattern') is None: missing.add(f'hatches.{material}')
    if rule_set.get('symbols.door.geometry') is None: missing.add('symbols.door')
    if rule_set.get('symbols.window.geometry') is None: missing.add('symbols.window')
    if rule_set.get('symbols.stair.geometry') is None: missing.add('symbols.stair')
    if rule_set.get('dimensions.rings') != 2: missing.add('dimensions.rings=2')
    if rule_set.get('levels.symbol') != 'triangle': missing.add('levels.symbol=triangle')
    return sorted(missing)
