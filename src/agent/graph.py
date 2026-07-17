from collections.abc import Callable

from langgraph.graph import END, START, StateGraph

from src.agent.nodes import (
    assemble_node,
    make_collect_node,
    make_evaluate_node,
    make_narrate_node,
)
from src.agent.state import AuditState
from src.collectors.base import Collector
from src.engine.models import AuditReport


def route_after_collect(state: AuditState) -> str:
    """Conditional edge: bail out if collection failed entirely."""
    return "abort" if "fatal_error" in state else "proceed"


def build_graph(collector: Collector, rules_path: str, narrator: Callable[[AuditReport], str]):
    g = StateGraph(AuditState)

    g.add_node("collect", make_collect_node(collector))
    g.add_node("assemble", assemble_node)
    g.add_node("evaluate", make_evaluate_node(rules_path))
    g.add_node("narrate", make_narrate_node(narrator))

    g.add_edge(START, "collect")
    g.add_conditional_edges("collect", route_after_collect, {"proceed": "assemble", "abort": END})
    g.add_edge("assemble", "evaluate")
    g.add_edge("evaluate", "narrate")
    g.add_edge("narrate", END)

    return g.compile()
