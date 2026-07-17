"""Deterministic markdown rendering of an AuditReport. No LLM, no network.
Used as the no-API-key fallback and as grounding material for the LLM."""

from src.engine.models import AuditReport, CheckResult, Status

_SEV_ORDER = {"high": 0, "medium": 1, "low": 2}


def _line(r: CheckResult) -> str:
    out = f"- **{r.rule_id}** ({r.severity.value}) {r.title} — CIS {r.cis_ref}\n"
    if r.status == Status.FAIL:
        out += f"  - actual: `{r.actual!r}`, expected: `{r.expected!r}`\n"
        out += f"  - remediation: {r.remediation}\n"
    elif r.status == Status.ERROR:
        out += f"  - could not assess: {r.message}\n"
    return out


def render_markdown(report: AuditReport) -> str:
    s = report.summary
    fails = sorted(
        (r for r in report.results if r.status == Status.FAIL),
        key=lambda r: _SEV_ORDER[r.severity.value],
    )
    errors = [r for r in report.results if r.status == Status.ERROR]
    passes = [r for r in report.results if r.status == Status.PASS]

    parts = [
        f"# Hardening Audit Report — {report.host}\n",
        f"**Results:** {s['pass']} pass / {s['fail']} fail / {s['error']} error\n",
    ]
    if fails:
        parts.append("\n## Failed checks (by severity)\n")
        parts += [_line(r) for r in fails]
    if errors:
        parts.append("\n## Could not assess\n")
        parts += [_line(r) for r in errors]
    if passes:
        parts.append("\n## Passed\n")
        parts += [f"- {r.rule_id} {r.title}\n" for r in passes]
    return "".join(parts)
