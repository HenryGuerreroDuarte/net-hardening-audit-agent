from src.engine.models import AuditReport, CheckResult, Rule, Status
from src.engine.operators import OPERATORS
from src.schema import HostSnapshot


def _lookup(data: dict, key: str | list[str]):
    """Resolve a key or nested key path. Raises KeyError if any step missing."""
    path = [key] if isinstance(key, str) else key
    current = data
    for part in path:
        if not isinstance(current, dict) or part not in current:
            raise KeyError(part)
        current = current[part]
    return current


def evaluate_rule(rule: Rule, snapshot: HostSnapshot) -> CheckResult:
    base = dict(
        rule_id=rule.id,
        title=rule.title,
        cis_ref=rule.cis_ref,
        severity=rule.severity,
        expected=rule.expected,
        remediation=rule.remediation,
    )

    # 1. Did collection for this source fail outright?
    if rule.source in snapshot.collection_errors:
        return CheckResult(
            **base,
            status=Status.ERROR,
            message=f"collection failed: {snapshot.collection_errors[rule.source]}",
        )

    # 2. Does the source exist at all?
    source_data = snapshot.sources.get(rule.source)
    if source_data is None:
        return CheckResult(
            **base, status=Status.ERROR, message=f"source '{rule.source}' not collected"
        )

    # 3. Resolve the setting.
    try:
        actual = _lookup(source_data, rule.key)
    except KeyError:
        return CheckResult(
            **base, status=Status.ERROR, message=f"setting '{rule.key}' not found in {rule.source}"
        )

    # 4. Compare.
    op = OPERATORS.get(rule.operator)
    if op is None:
        return CheckResult(
            **base,
            status=Status.ERROR,
            actual=actual,
            message=f"unknown operator '{rule.operator}'",
        )
    try:
        passed = op(actual, rule.expected)
    except ValueError as e:
        return CheckResult(
            **base, status=Status.ERROR, actual=actual, message=f"cannot evaluate: {e}"
        )

    return CheckResult(**base, actual=actual, status=Status.PASS if passed else Status.FAIL)


def run_audit(rules: list[Rule], snapshot: HostSnapshot) -> AuditReport:
    return AuditReport(host=snapshot.host, results=[evaluate_rule(r, snapshot) for r in rules])
