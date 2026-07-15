from datetime import UTC, datetime
from pathlib import Path

from .base import RawArtifact
from .commands import COMMANDS


class FixtureCollector:
    """Drop-in replacement for SSHCollector that reads saved files.
    Lets the full pipeline run with zero network access."""

    def __init__(self, fixture_dir: str = "tests/fixtures", host: str = "fixture-host"):
        self.dir = Path(fixture_dir)
        self.host = host

    def collect_all(self) -> list[RawArtifact]:
        artifacts = []
        for source, command in COMMANDS.items():
            path = self.dir / f"{source}.txt"
            artifacts.append(
                RawArtifact(
                    host=self.host,
                    source=source,
                    command=command,
                    stdout=path.read_text() if path.exists() else "",
                    stderr="" if path.exists() else "fixture missing",
                    exit_code=0 if path.exists() else 1,
                    collected_at=datetime.now(UTC),
                )
            )
        return artifacts
