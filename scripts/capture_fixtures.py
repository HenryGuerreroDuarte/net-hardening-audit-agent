"""Run once against the lab VM to snapshot real command output as fixtures.
Usage: python scripts/capture_fixtures.py <host> <user> <key_path>"""

import sys
from pathlib import Path

from src.collectors.ssh_collector import SSHCollector

host, user, key = sys.argv[1:4]
fixtures = Path("tests/fixtures")
fixtures.mkdir(parents=True, exist_ok=True)

for artifact in SSHCollector(host, user, key).collect_all():
    (fixtures / f"{artifact.source}.txt").write_text(artifact.stdout)
    print(f"captured {artifact.source}: {len(artifact.stdout)} bytes, exit {artifact.exit_code}")
