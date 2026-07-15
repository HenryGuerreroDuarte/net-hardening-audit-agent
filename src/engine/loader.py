from pathlib import Path

import yaml
from pydantic import ValidationError

from src.engine.models import Rule


def load_rules(path: str | Path) -> list[Rule]:
    raw = yaml.safe_load(Path(path).read_text())
    if not isinstance(raw, list):
        raise ValueError(f"{path}: expected a YAML list of rules")

    rules, errors = [], []
    for i, entry in enumerate(raw):
        try:
            rules.append(Rule(**entry))
        except ValidationError as e:
            errors.append(f"rule #{i} ({entry.get('id', '?')}): {e}")

    if errors:
        # fail loudly at load time — a malformed rule silently skipped
        # would mean a check you *think* is running but isn't
        raise ValueError("invalid rules:\n" + "\n".join(errors))

    ids = [r.id for r in rules]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate rule IDs found")
    return rules
