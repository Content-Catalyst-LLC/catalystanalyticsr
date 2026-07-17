#!/usr/bin/env python3
"""Generate a Catalyst Analytics R Markdown brief from scenario or comparison JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def load_payload(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def scenario_brief(payload: dict) -> str:
    inputs = payload.get("inputs", {})
    final = payload.get("final", {})
    notes = payload.get("interpretation_notes", [])
    canonical = payload.get("canonical_scenario", {})
    model = canonical.get("model", {})
    lines = [
        "# Catalyst Analytics R Scenario Brief", "",
        f"**Scenario:** {inputs.get('scenarioName', 'Untitled')}",
        f"**Time horizon:** {inputs.get('years', 'n/a')} years",
        f"**Composite score:** {payload.get('composite_score', 'n/a')}",
        f"**Budget ratio:** {payload.get('budget_ratio', 'n/a')}",
        f"**Scenario contract:** {canonical.get('schema_version', 'n/a')}",
        f"**Model:** {model.get('id', 'n/a')}@{model.get('version', 'n/a')}", "",
        "## Final-period values", "",
        f"- Produced capital: {final.get('produced_capital', 'n/a')}",
        f"- Human capital: {final.get('human_capital', 'n/a')}",
        f"- Natural capital: {final.get('natural_capital', 'n/a')}",
        f"- Cumulative emissions: {final.get('cumulative_emissions', 'n/a')}",
        f"- Adjusted savings: {final.get('adjusted_savings', 'n/a')}", "",
        "## Interpretation notes", "",
    ]
    lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Boundary", "", "This brief summarizes exploratory analysis. It is not a forecast, compliance determination, autonomous decision, or professional advice.", ""])
    return "\n".join(lines)


def comparison_brief(payload: dict) -> str:
    comparison = payload.get("comparison", payload)
    canonical = payload.get("canonical_scenarios", payload.get("scenarios", []))
    scenarios = {item.get("id"): item for item in canonical if isinstance(item, dict)}
    baseline_id = comparison.get("baseline_id", payload.get("baseline_id", "n/a"))
    policy_id = comparison.get("policy_id")
    if not policy_id:
        ids = [item for item in scenarios if item != baseline_id]
        policy_id = ids[0] if ids else "n/a"
    tradeoff = comparison.get("tradeoff", {})
    deltas = comparison.get("deltas", payload.get("deltas", []))
    notes = payload.get("interpretation_notes", [])
    lines = [
        "# Catalyst Analytics R Comparative Brief", "",
        f"**Baseline:** {scenarios.get(baseline_id, {}).get('title', baseline_id)}",
        f"**Comparison scenario:** {scenarios.get(policy_id, {}).get('title', policy_id)}",
        f"**Comparison contract:** {payload.get('schema_version', 'n/a')}",
        f"**Trade-off classification:** {tradeoff.get('classification', 'n/a')}", "",
        "## Metric deltas", "",
        "| Metric | Baseline | Scenario | Delta | Outcome |",
        "|---|---:|---:|---:|---|",
    ]
    for row in deltas:
        if row.get("scenario_id") and row.get("scenario_id") == baseline_id:
            continue
        lines.append(
            f"| {row.get('label', row.get('metric', 'n/a'))} | "
            f"{row.get('baseline_value', 'n/a')} | {row.get('policy_value', row.get('scenario_value', 'n/a'))} | "
            f"{row.get('absolute_delta', 'n/a')} | {row.get('outcome', 'n/a')} |"
        )
    lines.extend(["", "## Interpretation notes", ""])
    lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "## Boundary", "", "This brief summarizes exploratory comparative analysis. Rankings, dominance, and Pareto status are not autonomous recommendations or professional advice.", ""])
    return "\n".join(lines)


def brief(payload: dict) -> str:
    if "comparison" in payload or ("baseline_id" in payload and "deltas" in payload):
        return comparison_brief(payload)
    return scenario_brief(payload)


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
