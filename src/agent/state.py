from typing import TypedDict

from src.collectors.base import RawArtifact
from src.engine.models import AuditReport
from src.schema import HostSnapshot


class AuditState(TypedDict, total=False):
    """Shared state flowing through the graph. total=False because state
    starts empty and each node fills in its piece."""

    artifacts: list[RawArtifact]
    snapshot: HostSnapshot
    report: AuditReport
    narrative: str  # final human-readable report text
    fatal_error: str  # set only when the run cannot continue at all
