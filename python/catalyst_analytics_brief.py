#!/usr/bin/env python3
"""Generate a Catalyst Analytics R Markdown brief from governed analytics JSON exports."""

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


def climate_accounting_brief(payload: dict) -> str:
    is_browser = payload.get("export_type") == "browser_climate_accounting"
    if is_browser:
        title = "Browser climate, carbon, and natural-capital account"
        contract = payload.get("contract", {})
        carbon_pathway = payload.get("carbon_pathway", [])
        diagnostics = []
        if carbon_pathway:
            final = carbon_pathway[-1]
            diagnostics.append({
                "group": final.get("region", "Global"),
                "cumulative_net_emissions": final.get("cumulative_net_emissions"),
                "carbon_budget": final.get("carbon_budget"),
                "remaining_budget": final.get("remaining_budget"),
                "overshoot_time": next((row.get("year") for row in carbon_pathway if not row.get("within_budget", True)), None),
                "within_budget": final.get("within_budget"),
            })
        kaya = payload.get("kaya_decomposition", {})
        natural_rows = payload.get("natural_capital_account", [])
        boundaries = payload.get("boundary_assessment", [])
        package_version = contract.get("compatible_repository_version", "n/a")
        parity = contract.get("parity_status", "n/a")
    else:
        title = payload.get("title", payload.get("analysis_id", "Untitled climate account"))
        diagnostics = payload.get("carbon", {}).get("diagnostics", [])
        kaya = payload.get("kaya", {})
        natural_rows = payload.get("natural_capital", {}).get("data", [])
        boundaries = payload.get("boundary_assessment", {}).get("assessment", [])
        package_version = payload.get("package", {}).get("version", "n/a")
        parity = "r_package_accounting"

    lines = [
        "# Catalyst Analytics R Climate Accounting Brief", "",
        f"**Analysis:** {title}",
        f"**Package compatibility:** {package_version}",
        f"**Accounting boundary:** {parity}",
        f"**Schema version:** {payload.get('schema_version', 'n/a')}", "",
        "## Carbon-budget diagnostics", "",
        "| Scope | Cumulative net emissions | Budget | Remaining budget | Overshoot time | Status |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in diagnostics:
        status = "within budget" if row.get("within_budget") else "overshoot"
        lines.append(
            f"| {row.get('group', row.get('region', 'n/a'))} | "
            f"{row.get('cumulative_net_emissions', 'n/a')} | {row.get('carbon_budget', row.get('budget', 'n/a'))} | "
            f"{row.get('remaining_budget', 'n/a')} | {row.get('overshoot_time', 'n/a')} | {status} |"
        )
    if not diagnostics:
        lines.append("| n/a | n/a | n/a | n/a | n/a | no diagnostics |")

    contributions = kaya.get("contributions", []) if isinstance(kaya, dict) else []
    lines.extend(["", "## Kaya decomposition", ""])
    if contributions:
        for row in contributions:
            effects = []
            for key in ("population_effect", "affluence_effect", "energy_intensity_effect", "carbon_intensity_effect", "residual"):
                if key in row:
                    effects.append(f"{key.replace('_', ' ')}={row.get(key)}")
            label = row.get("group", row.get("region", row.get("period", "decomposition")))
            lines.append(f"- {label}: " + ", ".join(effects))
    else:
        lines.append("- No Kaya decomposition was included.")

    lines.extend(["", "## Natural-capital account", ""])
    if natural_rows:
        final_natural = natural_rows[-1]
        lines.extend([
            f"- Closing stock: {final_natural.get('closing_stock', 'n/a')} {final_natural.get('unit', '')}".rstrip(),
            f"- Net change: {final_natural.get('net_change', 'n/a')}",
            f"- Reconciliation error: {final_natural.get('reconciliation_error', 'n/a')}",
        ])
    else:
        lines.append("- No natural-capital account was included.")

    lines.extend(["", "## Boundary assessment", ""])
    if boundaries:
        for row in boundaries:
            lines.append(
                f"- {row.get('boundary_title', row.get('boundary_id', 'Boundary'))}: "
                f"{row.get('status', 'unknown')} (value={row.get('value', 'n/a')} {row.get('unit', '')})"
            )
    else:
        lines.append("- No boundary assessment was included.")

    lines.extend([
        "", "## Review boundary", "",
        "These accounts preserve declared sources, scopes, carbon-budget assumptions, GWP basis, and natural-capital accounting records. They are not forecasts, compliance determinations, autonomous decisions, or professional advice.", ""
    ])
    return "\n".join(lines)


def inclusive_development_brief(payload: dict) -> str:
    is_browser = payload.get("export_type") == "browser_inclusive_development"
    if is_browser:
        title = payload.get("inputs", {}).get("entity", "Browser inclusive development analysis")
        wealth = payload.get("inclusive_wealth", {})
        ans = payload.get("adjusted_net_savings", {})
        hdi = payload.get("human_development", {})
        distribution = payload.get("distribution", {}).get("summary", {})
        composite = payload.get("composite", {})
        contract = payload.get("contract", {})
        compatibility = contract.get("compatible_repository_version", "n/a")
    else:
        title = payload.get("title", payload.get("id", "Inclusive development analysis"))
        summary_rows = payload.get("summary", [])
        summary = summary_rows[-1] if isinstance(summary_rows, list) and summary_rows else summary_rows if isinstance(summary_rows, dict) else {}
        wealth_rows = payload.get("wealth", {}).get("data", [])
        final_wealth = wealth_rows[-1] if wealth_rows else {}
        wealth = {
            "closing": summary.get("closing_inclusive_wealth", final_wealth.get("inclusive_wealth")),
            "change": summary.get("inclusive_wealth_change", final_wealth.get("inclusive_wealth_change")),
            "per_capita_closing": summary.get("closing_per_capita_wealth", final_wealth.get("inclusive_wealth_per_capita")),
            "produced_share": final_wealth.get("produced_share"),
            "human_share": final_wealth.get("human_share"),
            "natural_share": final_wealth.get("natural_share"),
        }
        ans_rows = payload.get("adjusted_net_savings", [])
        ans = ans_rows[-1] if ans_rows else {}
        hdi_rows = payload.get("human_development", [])
        hdi = hdi_rows[-1] if hdi_rows else {}
        distribution = payload.get("distribution", {}).get("summary", {})
        scores = payload.get("composite", {}).get("scores", [])
        composite = {"score": scores[-1].get("composite_score") if scores else None}
        compatibility = payload.get("meta", {}).get("package_version", "n/a")
    lines = [
        "# Catalyst Analytics R Inclusive Development Brief", "",
        f"**Analysis:** {title}",
        f"**Package compatibility:** {compatibility}",
        f"**Schema version:** {payload.get('schema_version', 'n/a')}", "",
        "## Inclusive wealth", "",
        f"- Closing wealth: {wealth.get('closing', 'n/a')}",
        f"- Wealth change: {wealth.get('change', 'n/a')}",
        f"- Closing wealth per capita: {wealth.get('per_capita_closing', 'n/a')}",
        f"- Produced-capital share: {wealth.get('produced_share', 'n/a')}",
        f"- Human-capital share: {wealth.get('human_share', 'n/a')}",
        f"- Natural-capital share: {wealth.get('natural_share', 'n/a')}", "",
        "## Savings and human development", "",
        f"- Adjusted Net Savings: {ans.get('adjusted_net_savings', 'n/a')}",
        f"- Adjusted Net Savings as percent of GNI: {ans.get('adjusted_net_savings_percent_gni', 'n/a')}",
        f"- Life-expectancy index: {hdi.get('life_expectancy_index', 'n/a')}",
        f"- Education index: {hdi.get('education_index', 'n/a')}",
        f"- Income index: {hdi.get('income_index', 'n/a')}",
        f"- Human Development Index: {hdi.get('human_development_index', 'n/a')}", "",
        "## Distribution and composite score", "",
        f"- Gini: {distribution.get('gini', 'n/a')}",
        f"- Share below social floor: {distribution.get('share_below_social_floor', 'n/a')}",
        f"- Palma ratio: {distribution.get('palma_ratio', 'n/a')}",
        f"- Composite score: {composite.get('score', 'n/a')}", "",
        "## Review boundary", "",
        "Shadow prices, human-capital measurement, social floors, distribution weights, intergenerational discounting, and composite weights require explicit human review. This output is not a forecast, compliance determination, autonomous decision, or professional advice.", ""
    ]
    return "\n".join(lines)



def model_validation_brief(payload: dict) -> str:
    summary_rows = payload.get("summary", [])
    summary = summary_rows[-1] if isinstance(summary_rows, list) and summary_rows else summary_rows if isinstance(summary_rows, dict) else {}
    calibration = payload.get("calibration", {})
    validation = payload.get("validation", {})
    governance = payload.get("governance", {})
    card = governance.get("model_card", {})
    parameters = calibration.get("parameters", [])
    limitations = card.get("limitations", governance.get("limitations", []))
    lines = [
        "# Catalyst Analytics R Model Validation Brief", "",
        f"**Analysis:** {payload.get('title', payload.get('analysis_id', 'Model validation'))}",
        f"**Model:** {summary.get('model_id', calibration.get('model', {}).get('id', 'n/a'))}@{summary.get('model_version', calibration.get('model', {}).get('version', 'n/a'))}",
        f"**Validation status:** {summary.get('validation_status', validation.get('status', 'n/a'))}",
        f"**Lifecycle:** {summary.get('lifecycle_status', governance.get('lifecycle_status', 'n/a'))}", "",
        "## Calibrated parameters", "",
    ]
    if parameters:
        for row in parameters:
            lines.append(f"- {row.get('parameter', 'parameter')}: {row.get('estimate', 'n/a')} (initial {row.get('initial', 'n/a')}, bounds {row.get('lower', 'n/a')} to {row.get('upper', 'n/a')})")
    else:
        lines.append("- No calibrated parameters were included.")
    lines.extend(["", "## Validation evidence", "", f"- Calibration objective: {summary.get('calibration_objective', calibration.get('objective', 'n/a'))}", f"- Holdout RMSE: {summary.get('holdout_rmse', 'n/a')}", f"- Holdout MAE: {summary.get('holdout_mae', 'n/a')}", f"- Stability passed: {summary.get('stability_passed', 'n/a')}", "", "## Known limitations", ""])
    if limitations:
        for item in limitations:
            lines.append(f"- [{item.get('severity', 'unknown')}] {item.get('title', item.get('id', 'Limitation'))}: {item.get('description', '')}")
    else:
        lines.append("- No limitations were included.")
    lines.extend(["", "## Review boundary", "", "Calibration fit does not automatically establish causal validity, forecasting accuracy, compliance suitability, or professional fitness. Intended use, validation thresholds, numerical tolerances, limitations, and lifecycle approval require qualified human review.", ""])
    return "\n".join(lines)


def project_publication_brief(payload: dict) -> str:
    project = payload.get("project", payload)
    publication = payload.get("publication_manifest", payload.get("publication", {}))
    runs = project.get("runs", {})
    if isinstance(runs, list):
        run_rows = runs
    else:
        run_rows = list(runs.values())
    reviews = project.get("reviews", [])
    notes = project.get("notes", [])
    lines = [
        "# Catalyst Analytics R Project Publication Brief", "",
        f"**Project:** {project.get('title', project.get('id', 'Untitled'))}",
        f"**Project id:** {project.get('id', 'n/a')}",
        f"**Owner:** {project.get('owner', 'n/a')}",
        f"**Fingerprint:** {publication.get('project_fingerprint', 'n/a')}",
        f"**Package:** {publication.get('package', {}).get('version', project.get('metadata', {}).get('package_version', 'n/a'))}",
        f"**Review status:** {project.get('metadata', {}).get('review_status', 'n/a')}", "",
        "## Analytical purpose", "",
        project.get("description", "No description recorded."), "",
        "## Reproducibility record", "",
        f"- Scenarios: {len(project.get('scenarios', {}))}",
        f"- Datasets: {len(project.get('datasets', {}))}",
        f"- Models: {len(project.get('models', {}))}",
        f"- Runs: {len(run_rows)}",
        f"- Snapshots: {len(project.get('snapshots', []))}", "",
        "## Analytical runs", "",
    ]
    if run_rows:
        for run in run_rows:
            lines.append(f"- **{run.get('label', run.get('id', 'run'))}**: {run.get('status', 'n/a')}; input `{run.get('input_hash', 'n/a')}`; output `{run.get('output_hash', 'n/a')}`; review `{run.get('review_status', 'n/a')}`")
    else:
        lines.append("- No runs recorded.")
    lines.extend(["", "## Interpretation notes", ""])
    if notes:
        for note in notes:
            lines.append(f"- {note.get('text', '')}")
    else:
        lines.append("- No interpretation notes recorded.")
    lines.extend(["", "## Review record", ""])
    if reviews:
        for review in reviews:
            lines.append(f"- {review.get('reviewer', 'Reviewer')}: {review.get('decision', 'pending')}. {review.get('comments', '')}")
    else:
        lines.append("- No review records.")
    lines.extend(["", "## Publication boundary", "", "This brief preserves project inputs, run hashes, environment, interpretation, and review records. Reproducibility does not establish external validity, causal identification, compliance, fitness for use, or professional approval.", ""])
    return "\n".join(lines)

def brief(payload: dict) -> str:
    engine = payload.get("engine", {})
    if payload.get("export_type") in ("reproducible_analytical_project_publication", "browser_reproducible_project_publication") or payload.get("project_type") == "reproducible_analytical_project":
        return project_publication_brief(payload)
    if payload.get("export_type") in ("model_validation_governance", "browser_model_validation_governance") or payload.get("analysis_type") == "calibration_validation_model_governance":
        return model_validation_brief(payload)
    if payload.get("export_type") == "browser_inclusive_development" or payload.get("analysis_type") == "inclusive_wealth_human_development_distribution":
        return inclusive_development_brief(payload)
    if payload.get("export_type") == "browser_climate_accounting" or ("inventory" in payload and "carbon" in payload and "natural_capital" in payload):
        return climate_accounting_brief(payload)
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
