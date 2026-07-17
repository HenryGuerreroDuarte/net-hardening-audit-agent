from src.agent.graph import build_graph
from src.agent.render import render_markdown
from src.collectors.fixture_collector import FixtureCollector
from src.engine.models import Status

RULES = "rules/cis_ubuntu2204_l1.yaml"


def stub_narrator(report) -> str:
    return f"STUB NARRATIVE: {report.summary}"


class ExplodingCollector:
    def collect_all(self):
        raise ConnectionError("host unreachable")


def test_graph_end_to_end_offline():
    graph = build_graph(FixtureCollector(), RULES, stub_narrator)
    final = graph.invoke({})
    assert "fatal_error" not in final
    assert len(final["report"].results) >= 9
    assert final["narrative"].startswith("STUB NARRATIVE")


def test_graph_aborts_on_unreachable_host():
    graph = build_graph(ExplodingCollector(), RULES, stub_narrator)
    final = graph.invoke({})
    assert "fatal_error" in final
    assert "narrative" not in final  # narrate node never ran


def test_fallback_render_contains_evidence():
    graph = build_graph(FixtureCollector(), RULES, render_markdown)
    final = graph.invoke({})
    text = final["narrative"]
    assert "Hardening Audit Report" in text
    for r in final["report"].results:
        if r.status == Status.FAIL:
            assert r.rule_id in text  # every failure appears in output
