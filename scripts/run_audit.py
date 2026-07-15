"""Run the full pipeline offline: fixtures -> parse -> evaluate -> print.
Usage: python -m scripts.run_audit"""

from src.assemble import assemble
from src.collectors.fixture_collector import FixtureCollector
from src.engine.evaluator import run_audit
from src.engine.loader import load_rules

snapshot = assemble(FixtureCollector().collect_all())
report = run_audit(load_rules("rules/cis_ubuntu2204_l1.yaml"), snapshot)

for r in report.results:
    print(f"[{r.status.value.upper():5}] {r.rule_id:9} {r.title}")
    if r.status.value == "fail":
        print(f"        actual={r.actual!r} expected={r.expected!r}")
    elif r.status.value == "error":
        print(f"        {r.message}")

print(f"\nHost: {report.host}  |  {report.summary}")
