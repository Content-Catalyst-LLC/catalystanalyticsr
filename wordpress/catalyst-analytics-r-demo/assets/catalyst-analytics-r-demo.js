(function () {
  function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
  function round(value, digits) { var m = Math.pow(10, digits == null ? 2 : digits); return Math.round(value * m) / m; }
  function pct(value) { return Math.round(value * 100) + '%'; }
  function signed(value, digits) { var rounded = round(value, digits == null ? 1 : digits); return (rounded > 0 ? '+' : '') + rounded; }
  function slug(value) {
    var out = String(value || 'scenario').toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
    if (!out) out = 'scenario';
    if (!/^[a-z]/.test(out)) out = 'scenario-' + out;
    return out.slice(0, 80);
  }

  function scenarioInput(fd, prefix, fallbackName) {
    return {
      scenarioName: String(fd.get(prefix + 'Name') || fallbackName),
      role: prefix === 'baseline' ? 'baseline' : 'intervention',
      savings: Number(fd.get(prefix + 'Savings')) / 100,
      emissionsIntensity: Number(fd.get(prefix + 'EmissionsIntensity')) / 100,
      adaptation: Number(fd.get(prefix + 'Adaptation')) / 100,
      restoration: Number(fd.get(prefix + 'Restoration')) / 100,
      humanInvestment: Number(fd.get(prefix + 'HumanInvestment')) / 100
    };
  }

  function read(form) {
    var fd = new FormData(form);
    return {
      shared: {
        years: Number(fd.get('years') || 20),
        initialCapital: Number(fd.get('initialCapital') || 100),
        initialHuman: Number(fd.get('initialHuman') || 100),
        initialNatural: Number(fd.get('initialNatural') || 100),
        emissionsBudget: Number(fd.get('emissionsBudget') || 120)
      },
      baseline: scenarioInput(fd, 'baseline', 'Reference baseline'),
      policy: scenarioInput(fd, 'policy', 'Transition policy')
    };
  }

  function simulate(input, shared) {
    var rows = [];
    var K = shared.initialCapital, H = shared.initialHuman, N = shared.initialNatural, C = 0;
    var baseProductivity = 0.030, depreciation = 0.018, naturalDrag = 0.010;
    var adaptationProtection = 0.018 * input.adaptation;
    for (var year = 0; year <= shared.years; year++) {
      var output = 0.42 * K + 0.34 * H + 0.24 * N;
      var emissions = output * input.emissionsIntensity * (1 - 0.55 * input.adaptation);
      var depletion = Math.max(0, emissions * 0.30 - input.restoration * 8);
      var adjustedSavings = (input.savings * output) + (input.humanInvestment * output * 0.35) + (input.restoration * output * 0.25) - depletion - emissions * 0.15;
      var composite = (0.38 * K + 0.32 * H + 0.30 * N) - (0.18 * C);
      rows.push({
        year: year,
        produced_capital: round(K),
        human_capital: round(H),
        natural_capital: round(N),
        cumulative_emissions: round(C),
        adjusted_savings: round(adjustedSavings),
        composite_score: round(composite)
      });
      C += emissions;
      K += (baseProductivity + input.savings * 0.09) * K - depreciation * K;
      H += (0.012 + input.humanInvestment * 0.12) * H;
      N += input.restoration * 4 + adaptationProtection * 30 - naturalDrag * emissions - depletion * 0.05;
      N = Math.max(1, N);
    }
    var finalRow = rows[rows.length - 1];
    return {
      id: slug(input.scenarioName),
      input: input,
      trajectory: rows,
      final: finalRow,
      budget_ratio: finalRow.cumulative_emissions / Math.max(1, shared.emissionsBudget),
      within_budget: finalRow.cumulative_emissions <= shared.emissionsBudget
    };
  }

  var metricDefinitions = [
    { key: 'composite_score', label: 'Composite score', direction: 'higher_better' },
    { key: 'adjusted_savings', label: 'Adjusted savings', direction: 'higher_better' },
    { key: 'natural_capital', label: 'Natural capital', direction: 'higher_better' },
    { key: 'produced_capital', label: 'Produced capital', direction: 'higher_better' },
    { key: 'human_capital', label: 'Human capital', direction: 'higher_better' },
    { key: 'cumulative_emissions', label: 'Cumulative emissions', direction: 'lower_better' }
  ];

  function compare(inputs) {
    var baseline = simulate(inputs.baseline, inputs.shared);
    var policy = simulate(inputs.policy, inputs.shared);
    var deltas = metricDefinitions.map(function (definition) {
      var baselineValue = baseline.final[definition.key];
      var policyValue = policy.final[definition.key];
      var delta = policyValue - baselineValue;
      var improved = definition.direction === 'lower_better' ? delta < 0 : delta > 0;
      var outcome = Math.abs(delta) < 0.000001 ? 'tied' : improved ? 'improved' : 'worsened';
      return {
        metric: definition.key,
        label: definition.label,
        direction: definition.direction,
        baseline_value: baselineValue,
        policy_value: policyValue,
        absolute_delta: round(delta),
        percentage_delta: baselineValue === 0 ? null : round(delta / Math.abs(baselineValue), 4),
        outcome: outcome
      };
    });
    var improved = deltas.filter(function (row) { return row.outcome === 'improved'; });
    var worsened = deltas.filter(function (row) { return row.outcome === 'worsened'; });
    var classification = improved.length && !worsened.length ? 'dominates_baseline' :
      !improved.length && worsened.length ? 'dominated_by_baseline' :
      improved.length && worsened.length ? 'tradeoff' : 'equivalent';
    var baselineDominated = deltas.every(function (row) { return row.outcome !== 'worsened'; }) && improved.length > 0;
    var policyDominated = deltas.every(function (row) { return row.outcome !== 'improved'; }) && worsened.length > 0;
    return {
      baseline: baseline,
      policy: policy,
      deltas: deltas,
      tradeoff: {
        classification: classification,
        improved_metrics: improved.map(function (row) { return row.metric; }),
        worsened_metrics: worsened.map(function (row) { return row.metric; }),
        tied_metrics: deltas.filter(function (row) { return row.outcome === 'tied'; }).map(function (row) { return row.metric; })
      },
      pareto: {
        baseline_non_dominated: !baselineDominated,
        policy_non_dominated: !policyDominated
      }
    };
  }

  function canonicalScenario(input, shared, generatedAt) {
    var times = [];
    for (var year = 0; year <= shared.years; year++) times.push(year);
    return {
      schema_version: '1.0.0', id: slug(input.scenarioName), title: input.scenarioName, role: input.role,
      model: { id: 'khncpa', version: '1.0.0' },
      time: { start: 0, end: shared.years, step: 1, unit: 'year', values: times },
      initial_state: { K: shared.initialCapital, H: shared.initialHuman, N: shared.initialNatural, C: 0, P: 1, A: 1 },
      policy: { s: input.savings, e: input.humanInvestment, a: input.adaptation },
      parameters: { emissions_intensity: input.emissionsIntensity, regen: input.restoration },
      constraints: { emissions_budget: shared.emissionsBudget },
      units: {
        time: 'year',
        states: { K: 'index', H: 'index', N: 'index', C: 'index', P: 'people_index', A: 'index' },
        flows: { gdp: 'index', consumption: 'index', savings: 'index', education: 'index', abatement: 'share', emissions: 'tCO2e_index', depletion: 'index', damages: 'index' }
      },
      scope: { geography: { type: 'global', id: 'WORLD', label: 'Global' }, sectors: ['all'] },
      currency: { code: 'index', price_year: null }, sources: [],
      assumptions: [{ id: 'browser-comparison-mapping', statement: 'Browser controls map to the canonical KH-NC-PA scenario contract; browser equations are not numerically identical to the R engine.', status: 'declared' }],
      uncertainty: [], review: { status: 'draft', reviewed_by: [], notes: [] },
      metadata: { description: 'Generated by the Catalyst Analytics R comparative browser demo.', tags: ['browser', 'comparison'], created_by: 'catalyst-analytics-r-demo', created_at: generatedAt, browser_contract_version: '1.1.0' }
    };
  }

  function noteList(comparison, shared) {
    var notes = [];
    var tradeoff = comparison.tradeoff;
    if (tradeoff.classification === 'dominates_baseline') notes.push('The policy pathway improves every non-tied comparison metric in this simplified browser run.');
    else if (tradeoff.classification === 'dominated_by_baseline') notes.push('The policy pathway worsens every non-tied comparison metric; review the policy assumptions.');
    else if (tradeoff.classification === 'tradeoff') notes.push('The policy pathway improves some metrics and worsens others; the result requires an explicit trade-off decision.');
    else notes.push('The two pathways are equivalent across the selected comparison metrics.');
    if (comparison.policy.within_budget && !comparison.baseline.within_budget) notes.push('The policy pathway moves within the selected emissions budget while the baseline exceeds it.');
    else if (comparison.policy.within_budget) notes.push('Both pathways remain within the selected emissions budget; compare the remaining headroom.');
    else notes.push('The policy pathway still exceeds the selected emissions budget of ' + shared.emissionsBudget + '.');
    var natural = comparison.deltas.filter(function (row) { return row.metric === 'natural_capital'; })[0];
    if (natural.outcome === 'improved') notes.push('Policy assumptions preserve more natural capital than the baseline at the end of the horizon.');
    if (natural.outcome === 'worsened') notes.push('Policy assumptions leave less natural capital than the baseline at the end of the horizon.');
    notes.push('Treat the result as exploratory decision support, not a forecast or autonomous recommendation.');
    return notes;
  }

  function chart(svg, comparison, metric) {
    var width = 760, height = 320, left = 62, right = 28, top = 30, bottom = 52;
    var baselineRows = comparison.baseline.trajectory, policyRows = comparison.policy.trajectory;
    var values = baselineRows.concat(policyRows).map(function (row) { return row[metric]; });
    var minY = Math.min.apply(null, values), maxY = Math.max.apply(null, values);
    var pad = Math.max(1, (maxY - minY) * 0.10); minY -= pad; maxY += pad;
    function xScale(year) { return left + (year / comparison.baseline.trajectory[comparison.baseline.trajectory.length - 1].year) * (width - left - right); }
    function yScale(value) { return top + (1 - (value - minY) / Math.max(0.000001, maxY - minY)) * (height - top - bottom); }
    function path(rows) { return rows.map(function (row, index) { return (index ? 'L ' : 'M ') + xScale(row.year) + ' ' + yScale(row[metric]); }).join(' '); }
    var parts = ['<rect x="0" y="0" width="760" height="320" fill="#fbfaf6"/>'];
    for (var i = 0; i <= 4; i++) {
      var y = top + i * (height - top - bottom) / 4;
      parts.push('<line x1="' + left + '" y1="' + y + '" x2="' + (width-right) + '" y2="' + y + '" stroke="#d9d2c4"/>');
      parts.push('<text x="8" y="' + (y+4) + '">' + round(maxY - i * (maxY-minY)/4, 1) + '</text>');
    }
    parts.push('<line x1="' + left + '" y1="' + (height-bottom) + '" x2="' + (width-right) + '" y2="' + (height-bottom) + '" stroke="#000"/>');
    parts.push('<path d="' + path(baselineRows) + '" fill="none" stroke="#555555" stroke-width="3"/>');
    parts.push('<path d="' + path(policyRows) + '" fill="none" stroke="#9b1111" stroke-width="3"/>');
    parts.push('<line x1="' + left + '" y1="298" x2="' + (left+24) + '" y2="298" stroke="#555555" stroke-width="3"/><text x="' + (left+30) + '" y="302">Baseline</text>');
    parts.push('<line x1="' + (left+150) + '" y1="298" x2="' + (left+174) + '" y2="298" stroke="#9b1111" stroke-width="3"/><text x="' + (left+180) + '" y="302">Policy</text>');
    svg.innerHTML = parts.join('');
  }

  function render(root) {
    var form = root.querySelector('[data-scar-form]');
    var inputs = read(form), comparison = compare(inputs);
    var outputMap = {
      yearsOut: inputs.shared.years + ' years',
      baselineSavingsOut: pct(inputs.baseline.savings), baselineEmissionsOut: pct(inputs.baseline.emissionsIntensity), baselineAdaptOut: pct(inputs.baseline.adaptation), baselineRestoreOut: pct(inputs.baseline.restoration), baselineHumanOut: pct(inputs.baseline.humanInvestment),
      policySavingsOut: pct(inputs.policy.savings), policyEmissionsOut: pct(inputs.policy.emissionsIntensity), policyAdaptOut: pct(inputs.policy.adaptation), policyRestoreOut: pct(inputs.policy.restoration), policyHumanOut: pct(inputs.policy.humanInvestment)
    };
    Object.keys(outputMap).forEach(function (name) { root.querySelector('[data-out="' + name + '"]').textContent = outputMap[name]; });
    var scoreDelta = comparison.deltas.filter(function (row) { return row.metric === 'composite_score'; })[0];
    var ansDelta = comparison.deltas.filter(function (row) { return row.metric === 'adjusted_savings'; })[0];
    var emissionsDelta = comparison.deltas.filter(function (row) { return row.metric === 'cumulative_emissions'; })[0];
    root.querySelector('[data-result="scoreDelta"]').textContent = signed(scoreDelta.absolute_delta, 1);
    root.querySelector('[data-result="scoreNote"]').textContent = scoreDelta.outcome + ' versus baseline';
    root.querySelector('[data-result="ansDelta"]').textContent = signed(ansDelta.absolute_delta, 1);
    root.querySelector('[data-result="emissionsDelta"]').textContent = signed(emissionsDelta.absolute_delta, 1);
    root.querySelector('[data-result="budgetNote"]').textContent = comparison.policy.within_budget ? 'policy within budget' : 'policy over budget';
    root.querySelector('[data-result="tradeoff"]').textContent = comparison.tradeoff.classification.replace(/_/g, ' ');
    root.querySelector('[data-result="paretoNote"]').textContent = comparison.pareto.policy_non_dominated ? 'policy is non-dominated' : 'policy is dominated';
    root.querySelector('[data-comparison-table]').innerHTML = comparison.deltas.map(function (row) {
      return '<tr><th scope="row">' + row.label + '</th><td>' + row.baseline_value + '</td><td>' + row.policy_value + '</td><td>' + signed(row.absolute_delta, 2) + '</td><td data-outcome="' + row.outcome + '">' + row.outcome + '</td></tr>';
    }).join('');
    root.querySelector('[data-result="notes"]').innerHTML = noteList(comparison, inputs.shared).map(function (note) { return '<li>' + note + '</li>'; }).join('');
    chart(root.querySelector('[data-chart]'), comparison, root.querySelector('[data-chart-metric]').value);
    root._scarComparison = comparison; root._scarInputs = inputs;
  }

  function summary(comparison) {
    return [
      'Catalyst Analytics R comparative demo',
      'Baseline: ' + comparison.baseline.input.scenarioName,
      'Policy: ' + comparison.policy.input.scenarioName,
      'Trade-off status: ' + comparison.tradeoff.classification,
      'Improved metrics: ' + (comparison.tradeoff.improved_metrics.join(', ') || 'none'),
      'Worsened metrics: ' + (comparison.tradeoff.worsened_metrics.join(', ') || 'none'),
      'Policy cumulative emissions: ' + comparison.policy.final.cumulative_emissions,
      'Policy budget status: ' + (comparison.policy.within_budget ? 'within budget' : 'over budget'),
      'Boundary: exploratory browser comparison, not a forecast or professional advice.'
    ].join('\n');
  }

  function downloadJSON(root) {
    var inputs = root._scarInputs || read(root.querySelector('[data-scar-form]'));
    var comparison = root._scarComparison || compare(inputs);
    var generatedAt = new Date().toISOString();
    var payload = {
      schema_version: '1.2.0', demo: 'Catalyst Analytics R Demo', demo_version: '1.2.0',
      engine: { type: 'browser_simplified', compatible_repository_version: '0.3.0', parity_status: 'mapped_comparison_contract', comparison_contract_version: '1.0.0' },
      generated_at: generatedAt,
      inputs: inputs,
      canonical_scenarios: [canonicalScenario(inputs.baseline, inputs.shared, generatedAt), canonicalScenario(inputs.policy, inputs.shared, generatedAt)],
      comparison: {
        baseline_id: comparison.baseline.id, policy_id: comparison.policy.id,
        deltas: comparison.deltas, tradeoff: comparison.tradeoff, pareto: comparison.pareto,
        budget: { value: inputs.shared.emissionsBudget, baseline_within_budget: comparison.baseline.within_budget, policy_within_budget: comparison.policy.within_budget }
      },
      trajectories: { baseline: comparison.baseline.trajectory, policy: comparison.policy.trajectory },
      interpretation_notes: noteList(comparison, inputs.shared),
      boundary: { forecast: false, compliance: false, autonomous_decision: false, professional_advice: false }
    };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = 'catalyst-analytics-r-comparison.json';
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(function () { URL.revokeObjectURL(link.href); }, 500);
  }

  function init(root) {
    var form = root.querySelector('[data-scar-form]');
    form.addEventListener('input', function () { render(root); });
    root.querySelector('[data-chart-metric]').addEventListener('change', function () { render(root); });
    root.querySelector('[data-action="reset"]').addEventListener('click', function () { form.reset(); render(root); });
    root.querySelector('[data-action="download"]').addEventListener('click', function () { downloadJSON(root); });
    root.querySelector('[data-action="copy"]').addEventListener('click', function () {
      var text = summary(root._scarComparison || compare(read(form)));
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text); else window.prompt('Copy comparison:', text);
    });
    render(root);
  }

  document.addEventListener('DOMContentLoaded', function () { document.querySelectorAll('[data-scar-demo]').forEach(init); });
})();
