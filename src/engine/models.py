from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class Status(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"  # could not assess — missing data, bad rule, failed command


class Severity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Rule(BaseModel):
    id: str  # your stable ID, e.g. "SSH-001"
    title: str
    cis_ref: str = ""  # e.g. "5.2.7" — for traceability to the benchmark
    severity: Severity
    source: str  # which parsed source: "sshd_effective", "sysctl", ...
    key: str | list[str]  # setting key; list = nested path for file_perms
    operator: str  # name in the operator registry
    expected: Any = None
    remediation: str = ""


class CheckResult(BaseModel):
    rule_id: str
    title: str
    cis_ref: str
    severity: Severity
    status: Status
    actual: Any = None  # evidence: what the host actually had
    expected: Any = None
    message: str = ""  # human-readable detail, esp. for ERROR
    remediation: str = ""


class AuditReport(BaseModel):
    host: str
    results: list[CheckResult]

    @property
    def summary(self) -> dict[str, int]:
        counts = {s.value: 0 for s in Status}
        for r in self.results:
            counts[r.status.value] += 1
        return counts
