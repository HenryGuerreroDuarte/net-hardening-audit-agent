"""Run the full audit agent.
Offline:  python -m scripts.run_agent --fixtures
Live:     python -m scripts.run_agent --host 192.168.1.50 --user auditor --key ~/.ssh/audit_key
"""

import argparse
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv

from src.agent.graph import build_graph
from src.agent.llm import llm_available, pick_narrator
from src.collectors.fixture_collector import FixtureCollector
from src.collectors.ssh_collector import SSHCollector


def main():
    load_dotenv()  # pulls ANTHROPIC_API_KEY from .env before pick_narrator looks
    p = argparse.ArgumentParser()
    p.add_argument("--fixtures", action="store_true", help="run offline from tests/fixtures")
    p.add_argument("--host")
    p.add_argument("--user")
    p.add_argument("--key")
    p.add_argument("--rules", default="rules/cis_ubuntu2204_l1.yaml")
    args = p.parse_args()

    if args.fixtures:
        collector = FixtureCollector()
    elif args.host and args.user and args.key:
        collector = SSHCollector(args.host, args.user, args.key)
    else:
        p.error("use --fixtures, or provide --host --user --key")

    print(f"narrator: {'LLM' if llm_available() else 'deterministic fallback (no API key)'}")
    graph = build_graph(collector, args.rules, pick_narrator())
    final = graph.invoke({})

    if "fatal_error" in final:
        print(f"AUDIT ABORTED: {final['fatal_error']}")
        raise SystemExit(1)

    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out = Path("reports") / f"audit-{final['report'].host}-{stamp}.md"
    out.write_text(final["narrative"])
    print(f"summary: {final['report'].summary}")
    print(f"report written: {out}")


if __name__ == "__main__":
    main()
