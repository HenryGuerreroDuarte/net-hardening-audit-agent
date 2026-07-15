from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class RawArtifact:
    """One command's raw output from one host. Immutable on purpose —
    downstream code should never mutate collected evidence."""

    host: str
    source: str  # logical name, e.g. "sshd_effective"
    command: str  # exact command run, kept for the audit trail
    stdout: str
    stderr: str
    exit_code: int
    collected_at: datetime


class Collector(Protocol):
    def collect_all(self) -> list[RawArtifact]: ...
