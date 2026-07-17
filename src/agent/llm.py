"""LLM narration layer. The LLM receives the finished report as data and
writes prose around it. It cannot add, remove, or reclassify findings —
those exist before this module runs."""

import os

import anthropic

from src.agent.render import render_markdown
from src.engine.models import AuditReport

SYSTEM = """You are writing the narrative for a network hardening audit report.
You will receive the complete, final audit results as JSON. Rules:
- Base every statement ONLY on the JSON provided. Never invent, infer, or
  omit findings. Never change a finding's status or severity.
- Checks with status "error" were NOT assessed. State this plainly; do not
  guess whether they would pass.
- Structure: (1) Executive summary, 3-5 sentences, lead with overall risk
  posture. (2) Prioritized remediation plan ordered by severity then ease
  of fix, citing rule IDs and the actual vs expected evidence. (3) A short
  note listing unassessed checks and why coverage matters.
- Audience: a sysadmin who will act on this. Concrete, no filler."""


def llm_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def narrate_with_llm(report: AuditReport) -> str:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        temperature=0.2,
        system=SYSTEM,
        messages=[
            {"role": "user", "content": f"Audit results JSON:\n{report.model_dump_json(indent=2)}"}
        ],
    )
    narrative = "".join(b.text for b in response.content if b.type == "text")
    # Append the deterministic rendering as an appendix: the prose is the
    # LLM's, but the ground-truth table always ships with it.
    return narrative + "\n\n---\n\n## Appendix: raw findings\n\n" + render_markdown(report)


def pick_narrator():
    return narrate_with_llm if llm_available() else render_markdown
