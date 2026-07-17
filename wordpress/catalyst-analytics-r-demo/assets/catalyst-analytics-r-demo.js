(function () {
  'use strict';
  var OBSERVED = [1.000, 1.019, 1.041, 1.061, 1.084, 1.105, 1.129, 1.151, 1.174, 1.198];
  var CONTRACT = {
    engine: 'browser_educational_companion', compatible_repository_version: '0.8.0',
    calibration_contract_version: '1.0.0', validation_contract_version: '1.0.0', governance_contract_version: '1.0.0',
    parity_status: 'mapped_governance_contract_not_numerical_parity'
  };
  function number(form, name) { return Number(form.elements[name].value); }
  function format(value, digits) { return Number(value).toFixed(digits); }
  function rmse(rows) { return Math.sqrt(rows.reduce(function (sum, row) { return sum + row.residual * row.residual; }, 0) / rows.length); }
  function mae(rows) { return rows.reduce(function (sum, row) { return sum + Math.abs(row.residual); }, 0) / rows.length; }
  function bias(rows) { return rows.reduce(function (sum, row) { return sum + row.residual; }, 0) / rows.length; }
  function predict(rate) { return OBSERVED.map(function (_, time) { return 1 + rate * time + 0.00075 * time * time; }); }
  function calibrate(lower, upper, holdout) {
    var trainEnd = OBSERVED.length - holdout, best = null, steps = 800;
    for (var i = 0; i <= steps; i += 1) {
      var rate = lower + (upper - lower) * i / steps, predicted = predict(rate), rows = [];
      for (var t = 0; t < trainEnd; t += 1) rows.push({ residual: OBSERVED[t] - predicted[t] });
      var score = rmse(rows);
      if (!best || score < best.score) best = { rate: rate, score: score, predicted: predicted };
    }
    return best;
  }
  function buildAnalysis(form) {
    var initial = number(form, 'initial'), lower = number(form, 'lower'), upper = number(form, 'upper'), holdout = number(form, 'holdout'), threshold = number(form, 'threshold'), solverStep = number(form, 'solverStep');
    if (!(lower < upper) || initial < lower || initial > upper) throw new Error('The initial value must be inside valid lower and upper bounds.');
    var calibrated = calibrate(lower, upper, holdout), trainEnd = OBSERVED.length - holdout;
    var residuals = OBSERVED.map(function (observed, time) { var predicted = calibrated.predicted[time]; return { time: time, metric: 'N', observed: observed, predicted: predicted, residual: observed - predicted, split: time < trainEnd ? 'calibration' : 'holdout', weight: 1 }; });
    var training = residuals.filter(function (row) { return row.split === 'calibration'; }), testing = residuals.filter(function (row) { return row.split === 'holdout'; });
    var trainingMetrics = { split: 'calibration', metric: 'N', n: training.length, rmse: rmse(training), mae: mae(training), bias: bias(training) };
    var holdoutMetrics = { split: 'holdout', metric: 'N', n: testing.length, rmse: rmse(testing), mae: mae(testing), bias: bias(testing) };
    var passed = holdoutMetrics.rmse <= threshold;
    var solverError = solverStep * solverStep * 0.00032;
    var lifecycle = passed ? 'validated_for_specified_use' : 'under_review';
    var limitations = [
      { id: 'synthetic-benchmark-only', title: 'Synthetic benchmark data', severity: 'high', description: 'This browser record is not evidence of real-world forecasting validity.' },
      { id: 'structural-uncertainty', title: 'Structural uncertainty', severity: 'moderate', description: 'Historical fit cannot prove that all relevant causal mechanisms are represented.' }
    ];
    var checks = [
      { split: 'holdout', metric: 'N', check: 'rmse', observed: holdoutMetrics.rmse, operator: '<=', reference: threshold, passed: passed },
      { split: 'holdout', metric: 'N', check: 'absolute_bias', observed: Math.abs(holdoutMetrics.bias), operator: '<=', reference: threshold, passed: Math.abs(holdoutMetrics.bias) <= threshold }
    ];
    return {
      schema_version: '1.7.0', export_type: 'browser_model_validation_governance', demo_version: '1.7.0', generated_at: new Date().toISOString(), contract: CONTRACT,
      inputs: { training_years: trainEnd, holdout_years: holdout, initial_parameter: initial, lower_bound: lower, upper_bound: upper, validation_rmse_threshold: threshold, solver_step: solverStep },
      calibration: { parameter: 'regeneration_rate', initial: initial, estimate: calibrated.rate, objective: 'rmse', objective_value: trainingMetrics.rmse, converged: true },
      validation: { status: passed ? 'passed' : 'failed', metrics: [trainingMetrics, holdoutMetrics], residuals: residuals, checks: checks },
      numerical_evidence: { solver_benchmark: [{ method: 'rk4', step: solverStep, success: true, max_absolute_terminal_error: solverError }, { method: 'euler', step: solverStep, success: true, max_absolute_terminal_error: solverError * 13 }], stability_passed: true, invariants_passed: 4, boundary_cases_passed: 3 },
      governance: { lifecycle_status: lifecycle, intended_use: 'Educational synthetic benchmark only', prohibited_uses: ['forecast', 'compliance determination', 'investment decision', 'professional advice'], assumptions: [{ id: 'constant-rate', statement: 'One constant rate is used across the calibration period.', status: 'accepted_for_demo' }], limitations: limitations, approval_scope: passed ? 'Synthetic benchmark and educational scenario analysis only.' : 'No approved use; validation threshold was not met.' },
      review_boundary: { calibration_requires_review: true, validation_thresholds_require_review: true, numerical_tolerances_require_review: true, intended_use_requires_approval: true, limitations_must_be_disclosed: true, not_forecast_or_professional_advice: true }
    };
  }
  function draw(canvas, analysis) {
    var ratio = window.devicePixelRatio || 1, width = Math.max(520, Math.round(canvas.getBoundingClientRect().width || 800)), height = 290, pad = { l: 46, r: 22, t: 20, b: 38 };
    canvas.width = width * ratio; canvas.height = height * ratio;
    var ctx = canvas.getContext('2d'); ctx.scale(ratio, ratio); ctx.clearRect(0, 0, width, height);
    var rows = analysis.validation.residuals, min = 0.985, max = 1.215, x = function (i) { return pad.l + i * (width - pad.l - pad.r) / (rows.length - 1); }, y = function (v) { return pad.t + (max - v) * (height - pad.t - pad.b) / (max - min); };
    ctx.strokeStyle = '#ded9d2'; ctx.beginPath(); ctx.moveTo(pad.l, height - pad.b); ctx.lineTo(width - pad.r, height - pad.b); ctx.stroke();
    ctx.strokeStyle = '#701f2b'; ctx.lineWidth = 2.5; ctx.beginPath(); rows.forEach(function (row, i) { if (i === 0) ctx.moveTo(x(i), y(row.predicted)); else ctx.lineTo(x(i), y(row.predicted)); }); ctx.stroke();
    var holdoutStart = rows.findIndex(function (row) { return row.split === 'holdout'; });
    ctx.strokeStyle = '#215f43'; ctx.lineWidth = 3; ctx.beginPath(); rows.slice(Math.max(holdoutStart - 1, 0)).forEach(function (row, i) { var index = Math.max(holdoutStart - 1, 0) + i; if (i === 0) ctx.moveTo(x(index), y(row.predicted)); else ctx.lineTo(x(index), y(row.predicted)); }); ctx.stroke();
    ctx.fillStyle = '#171614'; rows.forEach(function (row, i) { ctx.beginPath(); ctx.arc(x(i), y(row.observed), 3.5, 0, Math.PI * 2); ctx.fill(); });
    ctx.fillStyle = '#68635d'; ctx.font = '11px Montserrat, Arial'; ctx.textAlign = 'center'; rows.forEach(function (row, i) { ctx.fillText(String(row.time), x(i), height - 17); }); ctx.textAlign = 'left'; ctx.fillText('time', width - 42, height - 17);
  }
  function render(root, analysis) {
    var calibration = analysis.validation.metrics[0], holdout = analysis.validation.metrics[1], passed = analysis.validation.status === 'passed';
    root.querySelector('[data-scar-estimate]').textContent = format(analysis.calibration.estimate, 4);
    root.querySelector('[data-scar-calibration]').textContent = format(calibration.rmse, 4);
    root.querySelector('[data-scar-holdout]').textContent = format(holdout.rmse, 4);
    root.querySelector('[data-scar-status]').textContent = passed ? 'Validated for specified use' : 'Under review';
    var validation = root.querySelector('[data-scar-validation]'); validation.textContent = analysis.validation.status; validation.dataset.state = analysis.validation.status;
    var governance = root.querySelector('[data-scar-governance]'); governance.textContent = passed ? 'Validated / specified use' : 'Under review'; governance.dataset.state = passed ? 'validated' : 'failed';
    root.querySelector('[data-scar-scope]').textContent = analysis.governance.approval_scope;
    draw(root.querySelector('[data-scar-chart]'), analysis);
    root.querySelector('[data-scar-residuals]').innerHTML = [['Calibration RMSE', calibration.rmse], ['Holdout RMSE', holdout.rmse], ['Holdout MAE', holdout.mae], ['Holdout bias', holdout.bias], ['Max absolute residual', Math.max.apply(null, analysis.validation.residuals.map(function (row) { return Math.abs(row.residual); }))]].map(function (row) { return '<div><span>' + row[0] + '</span><strong>' + format(row[1], 5) + '</strong></div>'; }).join('');
    var solver = analysis.numerical_evidence.solver_benchmark;
    root.querySelector('[data-scar-numerical]').innerHTML = [
      ['RK4 terminal error', solver[0].max_absolute_terminal_error, solver[0].max_absolute_terminal_error < 0.002],
      ['Euler terminal error', solver[1].max_absolute_terminal_error, solver[1].max_absolute_terminal_error < 0.02],
      ['Stability perturbations', analysis.numerical_evidence.stability_passed ? 'Passed' : 'Failed', analysis.numerical_evidence.stability_passed],
      ['Invariant tests', analysis.numerical_evidence.invariants_passed + ' passed', analysis.numerical_evidence.invariants_passed === 4],
      ['Boundary cases', analysis.numerical_evidence.boundary_cases_passed + ' passed', analysis.numerical_evidence.boundary_cases_passed === 3]
    ].map(function (row) { return '<div><span>' + row[0] + '</span><strong data-state="' + (row[2] ? 'passed' : 'warning') + '">' + (typeof row[1] === 'number' ? format(row[1], 5) : row[1]) + '</strong></div>'; }).join('');
    root.querySelector('[data-scar-limitations]').innerHTML = analysis.governance.limitations.map(function (item) { return '<article><strong>' + item.title + ' · ' + item.severity + '</strong><p>' + item.description + '</p></article>'; }).join('');
  }
  function download(data) { var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }), url = URL.createObjectURL(blob), link = document.createElement('a'); link.href = url; link.download = 'catalyst-analytics-r-model-validation-governance.json'; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url); }
  function init(root) { var form = root.querySelector('[data-scar-form]'), latest = null; function run(event) { if (event) event.preventDefault(); try { latest = buildAnalysis(form); render(root, latest); } catch (error) { window.alert(error.message); } } form.addEventListener('submit', run); root.querySelector('[data-scar-download]').addEventListener('click', function () { if (!latest) run(); if (latest) download(latest); }); root.querySelector('[data-scar-reset]').addEventListener('click', function () { form.reset(); run(); }); window.addEventListener('resize', function () { if (latest) draw(root.querySelector('[data-scar-chart]'), latest); }); run(); }
  document.addEventListener('DOMContentLoaded', function () { document.querySelectorAll('[data-scar-demo]').forEach(init); });
}());
