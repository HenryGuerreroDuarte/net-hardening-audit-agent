"""Graph nodes. Each takes AuditState, returns a partial state update.
Nodes that need dependencies (collector, rules, narrator) are built by
factory functions — dependency injection, so tests can swap any piece."""

from collections.abc import Callable

from src.agent.state import AuditState
from src.assemble import assemble
from src.collectors.base import Collector
from src.engine.evaluator import run_audit
from src.engine.loader import load_rules
from src.engine.models import AuditReport


def make_collect_node(collector: Collector):
    def collect_node(state: AuditState) -> AuditState:
        try:
            artifacts = collector.collect_all()
        except Exception as e:
            # host unreachable, auth failed, timeout — nothing to audit
            return {"fatal_error": f"collection failed: {type(e).__name__}: {e}"}
        if not artifacts or all(a.exit_code != 0 for a in artifacts):
            return {"fatal_error": "no usable output from any command"}
        return {"artifacts": artifacts}

    return collect_node


def assemble_node(state: AuditState) -> AuditState:
    return {"snapshot": assemble(state["artifacts"])}


def make_evaluate_node(rules_path: str):
    rules = load_rules(rules_path)  # load once at build time — fails loudly

    def evaluate_node(state: AuditState) -> AuditState:
        return {"report": run_audit(rules, state["snapshot"])}

    return evaluate_node


def make_narrate_node(narrator: Callable[[AuditReport], str]):
    def narrate_node(state: AuditState) -> AuditState:
        return {"narrative": narrator(state["report"])}

    return narrate_node
