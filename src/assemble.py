"""Turn raw collected artifacts into one normalized HostSnapshot."""

from src.collectors.base import RawArtifact
from src.parsers.files import parse_stat
from src.parsers.sshd import parse_sshd_effective
from src.parsers.sysctl import parse_sysctl
from src.schema import HostSnapshot

# source name -> parser function (replaces the string-based PARSERS
# placeholder in schema.py — actual callables, so no lookup magic)
PARSERS = {
    "sshd_effective": parse_sshd_effective,
    "sysctl": parse_sysctl,
    "file_perms": parse_stat,
}


def assemble(artifacts: list[RawArtifact]) -> HostSnapshot:
    sources: dict[str, dict] = {}
    errors: dict[str, str] = {}

    for a in artifacts:
        parser = PARSERS.get(a.source)
        if parser is None:
            continue  # collected but not yet parsed (e.g. sshd_config_raw) — fine
        if a.exit_code != 0:
            # failed command -> error, NOT an empty settings dict.
            # An empty dict would make every check on this source report
            # "setting missing"; an error routes them all to ERROR status.
            errors[a.source] = f"exit {a.exit_code}: {a.stderr.strip()[:200]}"
            continue
        sources[a.source] = parser(a.stdout)

    return HostSnapshot(
        host=artifacts[0].host if artifacts else "unknown",
        collected_at=min(a.collected_at for a in artifacts) if artifacts else None,
        sources=sources,
        collection_errors=errors,
    )
