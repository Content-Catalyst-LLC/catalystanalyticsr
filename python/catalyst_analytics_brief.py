#!/usr/bin/env python3
"""Generate a Catalyst Analytics R Markdown brief from scenario, comparison, uncertainty, or data-analysis JSON."""

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



def uncertainty_brief(payload: dict) -> str:
    scenario = payload.get("scenario", {})
    model = scenario.get("model", {})
    meta = payload.get("meta", {})
    summary = payload.get("summary", [])
    probabilities = payload.get("probabilities", [])
    sensitivity = sorted(
        payload.get("sensitivity", []),
        key=lambda row: row.get("absolute_effect", 0) or 0,
        reverse=True,
    )
    lines = [
        "# Catalyst Analytics R Uncertainty Brief", "",
        f"**Scenario:** {scenario.get('title', scenario.get('id', 'Untitled'))}",
        f"**Model:** {model.get('id', 'n/a')}@{model.get('version', 'n/a')}",
        f"**Sampling:** {meta.get('sampling', 'n/a')}",
        f"**Seed:** {meta.get('seed', 'n/a')}",
        f"**Completed:** {meta.get('completed', 'n/a')} of {meta.get('requested', 'n/a')}",
        f"**Failed:** {meta.get('failed', 'n/a')} ({meta.get('failure_rate', 'n/a')})", "",
        "## Uncertainty intervals", "",
        "| Metric | Mean | P10 | Median | P90 | Unit |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in summary:
        lines.append(
            f"| {row.get('metric', 'n/a')} | {row.get('mean', 'n/a')} | "
            f"{row.get('p10', 'n/a')} | {row.get('median', 'n/a')} | "
            f"{row.get('p90', 'n/a')} | {row.get('unit', 'n/a')} |"
        )
    lines.extend(["", "## Threshold probabilities", ""])
    if probabilities:
        for row in probabilities:
            lines.append(
                f"- {row.get('metric', 'n/a')} {row.get('operator', '')} "
                f"{row.get('threshold', 'n/a')}: {row.get('probability', 'n/a')}"
            )
    else:
        lines.append("- No threshold probabilities were requested.")
    lines.extend(["", "## Strongest sensitivity signals", ""])
    if sensitivity:
        for row in sensitivity[:10]:
            lines.append(
                f"- {row.get('target', 'n/a')} -> {row.get('metric', 'n/a')}: "
                f"{row.get('estimate', 'n/a')} ({row.get('method', 'n/a')})"
            )
    else:
        lines.append("- No sensitivity estimates were available.")
    lines.extend([
        "", "## Boundary", "",
        "This brief summarizes sampled exploratory analysis. Intervals and probabilities depend on the declared distributions, model structure, and available evidence. They are not forecasts, compliance determinations, autonomous decisions, or professional advice.", ""
    ])
    return "\n".join(lines)


def data_analysis_brief(payload: dict) -> str:
    dataset = payload.get("dataset", {})
    quality = payload.get("quality", dataset.get("quality", {}))
    indicators = payload.get("indicators", payload.get("indicator_registry", []))
    values = payload.get("indicator_values", payload.get("indicator_result", {}).get("values", []))
    source = dataset.get("source", {})
    lines = [
        "# Catalyst Analytics R Data and Indicator Brief", "",
        f"**Dataset:** {dataset.get('title', dataset.get('id', 'Untitled'))}",
        f"**Dataset id:** {dataset.get('id', 'n/a')}",
        f"**Source:** {source.get('title', 'n/a')}",
        f"**Publisher:** {source.get('publisher', 'n/a')}",
        f"**License:** {source.get('license', 'n/a')}",
        f"**Rows:** {quality.get('row_count', len(dataset.get('records', dataset.get('data', []))))}",
        f"**Columns:** {quality.get('column_count', 'n/a')}",
        f"**Missing cells:** {quality.get('missing_cells', 'n/a')}",
        f"**Duplicate keys:** {quality.get('duplicate_keys', 'n/a')}", "",
        "## Indicator definitions", "",
        "| Indicator | Version | Formula | Unit | Direction |",
        "|---|---|---|---|---|",
    ]
    for item in indicators:
        lines.append(
            f"| {item.get('title', item.get('id', 'n/a'))} | {item.get('version', 'n/a')} | "
            f"`{item.get('formula', 'n/a')}` | {item.get('unit', 'n/a')} | {item.get('direction', 'n/a')} |"
        )
    lines.extend(["", "## Calculated values", ""])
    if values:
        for row in values[:20]:
            identity = ", ".join(
                f"{key}={row.get(key)}" for key in ("region", "year", "indicator") if key in row
            )
            lines.append(f"- {identity or 'value'}: {row.get('value', 'n/a')}")
        if len(values) > 20:
            lines.append(f"- ... and {len(values) - 20} additional value(s).")
    else:
        lines.append("- No calculated values were included.")
    flags = quality.get("flags", [])
    lines.extend(["", "## Data-quality flags", ""])
    if flags:
        for flag in flags:
            lines.append(f"- [{flag.get('severity', 'info')}] {flag.get('message', flag.get('code', 'flag'))}")
    else:
        lines.append("- No quality flags were included.")
    lines.extend([
        "", "## Boundary", "",
        "This brief preserves declared source, quality, unit, and indicator metadata. It does not verify source truth, licensing rights, unit comparability, causal interpretation, or fitness for a specific decision.", ""
    ])
    return "\n".join(lines)

def brief(payload: dict) -> str:
    engine = payload.get("engine", {})
    if "dataset" in payload and ("indicators" in payload or "indicator_registry" in payload or engine.get("type") == "browser_data_intake"):
        return data_analysis_brief(payload)
    if payload.get("analysis_type") == "uncertainty_ensemble":
        return uncertainty_brief(payload)
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
