from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _usage_block(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    marker = r"\usage{"
    start = text.find(marker)
    assert start >= 0, f"missing usage block: {path.name}"
    i = start + len(marker)
    depth = 0
    in_string = None
    escaped = False
    for j in range(i, len(text)):
        char = text[j]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if in_string:
            if char == in_string:
                in_string = None
            continue
        if char in ("'", '"'):
            in_string = char
        elif char == "{":
            depth += 1
        elif char == "}":
            if depth == 0:
                return text[i:j]
            depth -= 1
    raise AssertionError(f"unterminated usage block: {path.name}")


def _assert_balanced_parentheses(text: str) -> None:
    depth = 0
    in_string = None
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if in_string:
            if char == in_string:
                in_string = None
            continue
        if char in ("'", '"'):
            in_string = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            assert depth >= 0, "usage closes a parenthesis before opening one"
    assert depth == 0, "usage has unbalanced parentheses"
    assert in_string is None, "usage has an unterminated string"


def test_econometrics_rd_usage_uses_real_line_breaks_and_valid_calls():
    path = ROOT / "man/econometrics_policy_evaluation.Rd"
    usage = _usage_block(path)
    assert r"\n" not in usage
    assert usage.count("\n") >= 20
    for name in (
        "causal_assumption", "regression_spec", "validate_regression_spec",
        "fit_policy_regression", "panel_regression", "regression_diagnostics",
        "difference_in_differences", "event_study", "interrupted_time_series",
        "synthetic_control", "policy_effect_summary", "policy_evaluation_analysis",
        "policy_evaluation_summary", "plot_policy_effects", "plot_event_study",
        "plot_synthetic_control"
    ):
        assert f"{name}(" in usage
    _assert_balanced_parentheses(usage)


def test_workspace_policy_evaluation_rd_usage_uses_real_line_breaks():
    path = ROOT / "man/workspace_policy_evaluations.Rd"
    usage = _usage_block(path)
    assert r"\n" not in usage
    assert "workspace_add_policy_evaluation(workspace, analysis, replace = FALSE)" in usage
    assert "workspace_get_policy_evaluation(workspace, evaluation_id)" in usage
    _assert_balanced_parentheses(usage)
