#!/usr/bin/env python3
"""Generate a short Catalyst Analytics R brief from a demo JSON export."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def brief(payload: dict) -> str:
    inputs = payload.get("inputs", {})
    final = payload.get("final", {})
    notes = payload.get("interpretation_notes", [])
    lines = [
        "# Catalyst Analytics R Scenario Brief",
        "",
        f"**Scenario:** {inputs.get('scenarioName', 'Untitled')}",
        f"**Time horizon:** {inputs.get('years', 'n/a')} years",
        f"**Composite score:** {payload.get('composite_score', 'n/a')}",
        f"**Budget ratio:** {payload.get('budget_ratio', 'n/a')}",
        "",
        "## Final-period values",
        "",
        f"- Produced capital: {final.get('produced_capital', 'n/a')}",
        f"- Human capital: {final.get('human_capital', 'n/a')}",
        f"- Natural capital: {final.get('natural_capital', 'n/a')}",
        f"- Cumulative emissions: {final.get('cumulative_emissions', 'n/a')}",
        f"- Adjusted savings: {final.get('adjusted_savings', 'n/a')}",
        "",
        "## Interpretation notes",
        "",
    ]
    lines.extend(f"- {note}" for note in notes)
    lines.extend([
        "",
        "## Boundary",
        "",
        "This brief summarizes an exploratory browser demo export. It is not a forecast, certification, compliance determination, or professional advice.",
        "",
    ])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: catalyst_analytics_brief.py input.json output.md", file=sys.stderr)
        return 2
    payload = load_payload(Path(argv[1]))
    Path(argv[2]).write_text(brief(payload), encoding="utf-8")
    print(f"wrote {argv[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
