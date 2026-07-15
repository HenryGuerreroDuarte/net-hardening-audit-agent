from datetime import UTC, datetime

import pytest

from src.engine.evaluator import evaluate_rule
from src.engine.loader import load_rules
from src.engine.models import Rule, Severity, Status
from src.engine.operators import op_equals, op_in, op_max
from src.schema import HostSnapshot


def make_snapshot(sources=None, errors=None) -> HostSnapshot:
    return HostSnapshot(
        host="test",
        collected_at=datetime.now(UTC),
        sources=sources or {},
        collection_errors=errors or {},
    )


def make_rule(**overrides) -> Rule:
    base = dict(
        id="T-001",
        title="test",
        severity=Severity.LOW,
        source="sshd_effective",
        key="permitrootlogin",
        operator="equals",
        expected="no",
    )
    return Rule(**{**base, **overrides})


# --- operators ---


def test_equals_is_case_insensitive():
    assert op_equals("No", "no")


def test_max_numeric():
    assert op_max("3", 4)
    assert not op_max("6", 4)


def test_max_raises_on_garbage():
    with pytest.raises(ValueError):
        op_max("banana", 4)


def test_in_normalizes_case():
    assert op_in("INFO", ["info", "verbose"])


def test_in_accepts_single_string_expected():
    assert op_in("INFO", "info")
    assert not op_in("DEBUG", "info")


# --- evaluator: the three states ---


def test_pass():
    snap = make_snapshot({"sshd_effective": {"permitrootlogin": "no"}})
    assert evaluate_rule(make_rule(), snap).status == Status.PASS


def test_fail_carries_evidence():
    snap = make_snapshot({"sshd_effective": {"permitrootlogin": "yes"}})
    result = evaluate_rule(make_rule(), snap)
    assert result.status == Status.FAIL
    assert result.actual == "yes"


def test_missing_key_is_error_not_fail():
    snap = make_snapshot({"sshd_effective": {}})
    assert evaluate_rule(make_rule(), snap).status == Status.ERROR


def test_collection_failure_is_error():
    snap = make_snapshot(errors={"sshd_effective": "exit 1: sudo: a password is required"})
    result = evaluate_rule(make_rule(), snap)
    assert result.status == Status.ERROR
    assert "collection failed" in result.message


def test_nested_key_path():
    snap = make_snapshot({"file_perms": {"/etc/passwd": {"mode": "644"}}})
    rule = make_rule(source="file_perms", key=["/etc/passwd", "mode"], operator="max", expected=644)
    assert evaluate_rule(rule, snap).status == Status.PASS


# --- loader + real rules against real fixtures ---


def test_rule_file_loads_and_validates():
    rules = load_rules("rules/cis_ubuntu2204_l1.yaml")
    assert len(rules) >= 9
    assert len({r.id for r in rules}) == len(rules)
