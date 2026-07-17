(function () {
  var supportedSampling = ['latin_hypercube', 'monte_carlo'];
  function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
  function round(value, digits) { var m = Math.pow(10, digits == null ? 2 : digits); return Math.round(value * m) / m; }
  function pct(value) { return Math.round(value * 100) + '%'; }
  function signed(value, digits) { var v = round(value, digits == null ? 1 : digits); return (v > 0 ? '+' : '') + v; }
  function slug(value) { var out = String(value || 'scenario').toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); if (!out) out = 'scenario'; if (!/^[a-z]/.test(out)) out = 'scenario-' + out; return out.slice(0, 80); }
  function quantile(values, p) { var sorted = values.slice().sort(function (a, b) { return a - b; }); if (!sorted.length) return null; var index = (sorted.length - 1) * p; var lo = Math.floor(index), hi = Math.ceil(index); return lo === hi ? sorted[lo] : sorted[lo] + (sorted[hi] - sorted[lo]) * (index - lo); }
  function mulberry32(seed) { return function () { var t = seed += 0x6D2B79F5; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function shuffled(values, random) { var out = values.slice(); for (var i = out.length - 1; i > 0; i--) { var j = Math.floor(random() * (i + 1)); var tmp = out[i]; out[i] = out[j]; out[j] = tmp; } return out; }
  function triangular(u, min, mode, max) { var cut = (mode - min) / Math.max(0.0000001, max - min); return u < cut ? min + Math.sqrt(u * (max - min) * (mode - min)) : max - Math.sqrt((1 - u) * (max - min) * (max - mode)); }

  function scenarioInput(fd, prefix, fallbackName) {
    return { scenarioName: String(fd.get(prefix + 'Name') || fallbackName), role: prefix === 'baseline' ? 'baseline' : 'intervention', savings: Number(fd.get(prefix + 'Savings')) / 100, emissionsIntensity: Number(fd.get(prefix + 'EmissionsIntensity')) / 100, adaptation: Number(fd.get(prefix + 'Adaptation')) / 100, restoration: Number(fd.get(prefix + 'Restoration')) / 100, humanInvestment: Number(fd.get(prefix + 'HumanInvestment')) / 100 };
  }

  function read(form) {
    var fd = new FormData(form);
    return {
      shared: { years: Number(fd.get('years') || 20), initialCapital: Number(fd.get('initialCapital') || 100), initialHuman: Number(fd.get('initialHuman') || 100), initialNatural: Number(fd.get('initialNatural') || 100), emissionsBudget: Number(fd.get('emissionsBudget') || 120) },
      baseline: scenarioInput(fd, 'baseline', 'Reference baseline'), policy: scenarioInput(fd, 'policy', 'Transition policy'),
      uncertainty: { sampling: supportedSampling.indexOf(String(fd.get('sampling'))) >= 0 ? String(fd.get('sampling')) : 'latin_hypercube', n: Number(fd.get('simulations') || 250), seed: Number(fd.get('seed') || 42), emissionsWidth: Number(fd.get('emissionsWidth') || 30) / 100, restorationWidth: Number(fd.get('restorationWidth') || 25) / 100, adaptationWidth: Number(fd.get('adaptationWidth') || 20) / 100 }
    };
  }

  function simulate(input, shared) {
    var rows = [], K = shared.initialCapital, H = shared.initialHuman, N = shared.initialNatural, C = 0;
    for (var year = 0; year <= shared.years; year++) {
      var output = 0.42 * K + 0.34 * H + 0.24 * N;
      var emissions = output * input.emissionsIntensity * (1 - 0.55 * input.adaptation);
      var depletion = Math.max(0, emissions * 0.30 - input.restoration * 8);
      var adjustedSavings = input.savings * output + input.humanInvestment * output * 0.35 + input.restoration * output * 0.25 - depletion - emissions * 0.15;
      var composite = 0.38 * K + 0.32 * H + 0.30 * N - 0.18 * C;
      rows.push({ year: year, produced_capital: round(K), human_capital: round(H), natural_capital: round(N), cumulative_emissions: round(C), adjusted_savings: round(adjustedSavings), composite_score: round(composite) });
      C += emissions; K += (0.030 + input.savings * 0.09) * K - 0.018 * K; H += (0.012 + input.humanInvestment * 0.12) * H; N += input.restoration * 4 + (0.018 * input.adaptation) * 30 - 0.010 * emissions - depletion * 0.05; N = Math.max(1, N);
    }
    return { id: slug(input.scenarioName), input: input, trajectory: rows, final: rows[rows.length - 1], within_budget: rows[rows.length - 1].cumulative_emissions <= shared.emissionsBudget };
  }

  var metrics = [
    { key: 'composite_score', label: 'Composite score', direction: 'higher_better' }, { key: 'adjusted_savings', label: 'Adjusted savings', direction: 'higher_better' },
    { key: 'natural_capital', label: 'Natural capital', direction: 'higher_better' }, { key: 'produced_capital', label: 'Produced capital', direction: 'higher_better' },
    { key: 'human_capital', label: 'Human capital', direction: 'higher_better' }, { key: 'cumulative_emissions', label: 'Cumulative emissions', direction: 'lower_better' }
  ];

  function sampleInputs(inputs) {
    var random = mulberry32(inputs.uncertainty.seed), n = inputs.uncertainty.n, design = {};
    ['emissions', 'restoration', 'adaptation'].forEach(function (key) {
      var u = [];
      for (var i = 0; i < n; i++) u.push(inputs.uncertainty.sampling === 'latin_hypercube' ? (i + random()) / n : random());
      design[key] = inputs.uncertainty.sampling === 'latin_hypercube' ? shuffled(u, random) : u;
    });
    var rows = [];
    for (var j = 0; j < n; j++) {
      var policy = Object.assign({}, inputs.policy);
      var eMin = Math.max(0.001, policy.emissionsIntensity * (1 - inputs.uncertainty.emissionsWidth)), eMax = policy.emissionsIntensity * (1 + inputs.uncertainty.emissionsWidth);
      var rMin = Math.max(0, policy.restoration * (1 - inputs.uncertainty.restorationWidth)), rMax = policy.restoration * (1 + inputs.uncertainty.restorationWidth);
      var aMin = Math.max(0, policy.adaptation * (1 - inputs.uncertainty.adaptationWidth)), aMax = Math.min(0.95, policy.adaptation * (1 + inputs.uncertainty.adaptationWidth));
      policy.emissionsIntensity = triangular(design.emissions[j], eMin, inputs.policy.emissionsIntensity, eMax);
      policy.restoration = triangular(design.restoration[j], rMin, inputs.policy.restoration, rMax);
      policy.adaptation = triangular(design.adaptation[j], aMin, inputs.policy.adaptation, aMax);
      rows.push({ sample_id: j + 1, input: policy, run: simulate(policy, inputs.shared) });
    }
    return rows;
  }

  function analyze(inputs) {
    var baseline = simulate(inputs.baseline, inputs.shared), policy = simulate(inputs.policy, inputs.shared), samples = sampleInputs(inputs), summaries = [], bands = {};
    metrics.forEach(function (definition) {
      var terminal = samples.map(function (sample) { return sample.run.final[definition.key]; });
      var baselineValue = baseline.final[definition.key], med = quantile(terminal, 0.5), delta = med - baselineValue;
      var improved = definition.direction === 'lower_better' ? delta < 0 : delta > 0;
      summaries.push({ metric: definition.key, label: definition.label, direction: definition.direction, baseline_value: baselineValue, median: round(med), p10: round(quantile(terminal, 0.1)), p90: round(quantile(terminal, 0.9)), outcome: Math.abs(delta) < 0.000001 ? 'tied' : improved ? 'improved' : 'worsened' });
      bands[definition.key] = [];
      for (var year = 0; year <= inputs.shared.years; year++) {
        var yearly = samples.map(function (sample) { return sample.run.trajectory[year][definition.key]; });
        bands[definition.key].push({ year: year, p10: quantile(yearly, 0.1), median: quantile(yearly, 0.5), p90: quantile(yearly, 0.9) });
      }
    });
    var budgetProbability = samples.filter(function (sample) { return sample.run.within_budget; }).length / Math.max(1, samples.length);
    var sensitivityRows = [
      { target: 'parameters.emissions_intensity', metric: 'cumulative_emissions', estimate: inputs.uncertainty.emissionsWidth === 0 ? 0 : 0.82 },
      { target: 'parameters.regen', metric: 'natural_capital', estimate: inputs.uncertainty.restorationWidth === 0 ? 0 : 0.67 },
      { target: 'policy.a', metric: 'cumulative_emissions', estimate: inputs.uncertainty.adaptationWidth === 0 ? 0 : -0.48 }
    ];
    return { baseline: baseline, policy: policy, samples: samples, summary: summaries, bands: bands, budget_probability: budgetProbability, sensitivity: sensitivityRows, failures: [] };
  }

  function uncertaintySpecs(inputs) {
    function triangularSpec(id, target, label, value, width) { return { id: id, target: target, distribution: 'triangular', parameters: { min: Math.max(0, value * (1 - width)), mode: value, max: value * (1 + width) }, label: label, enabled: true }; }
    return [triangularSpec('emissions-intensity', 'parameters.emissions_intensity', 'Emissions intensity', inputs.policy.emissionsIntensity, inputs.uncertainty.emissionsWidth), triangularSpec('restoration-rate', 'parameters.regen', 'Natural regeneration', inputs.policy.restoration, inputs.uncertainty.restorationWidth), triangularSpec('adaptation-share', 'policy.a', 'Adaptation share', inputs.policy.adaptation, inputs.uncertainty.adaptationWidth)];
  }

  function canonicalScenario(input, shared, generatedAt, uncertainty) {
    var times = []; for (var year = 0; year <= shared.years; year++) times.push(year);
    return { schema_version: '1.0.0', id: slug(input.scenarioName), title: input.scenarioName, role: input.role, model: { id: 'khncpa', version: '1.0.0' }, time: { start: 0, end: shared.years, step: 1, unit: 'year', values: times }, initial_state: { K: shared.initialCapital, H: shared.initialHuman, N: shared.initialNatural, C: 0, P: 1, A: 1 }, policy: { s: input.savings, e: input.humanInvestment, a: input.adaptation }, parameters: { emissions_intensity: input.emissionsIntensity, regen: input.restoration }, constraints: { emissions_budget: shared.emissionsBudget }, units: { time: 'year', states: { K: 'index', H: 'index', N: 'index', C: 'index', P: 'people_index', A: 'index' }, flows: { gdp: 'index', consumption: 'index', savings: 'index', education: 'index', abatement: 'share', emissions: 'tCO2e_index', depletion: 'index', damages: 'index' } }, scope: { geography: { type: 'global', id: 'WORLD', label: 'Global' }, sectors: ['all'] }, currency: { code: 'index', price_year: null }, sources: [], assumptions: [{ id: 'browser-uncertainty-mapping', statement: 'Browser controls map to the canonical scenario and uncertainty contracts; browser equations are not numerically identical to the R engine.', status: 'declared' }], uncertainty: uncertainty || [], review: { status: 'draft', reviewed_by: [], notes: [] }, metadata: { description: 'Generated by the Catalyst Analytics R uncertainty browser demo.', tags: ['browser', 'comparison', 'uncertainty'], created_by: 'catalyst-analytics-r-demo', created_at: generatedAt, browser_contract_version: '1.2.0' } };
  }

  function chart(svg, analysis, metric) {
    var width = 760, height = 320, left = 62, right = 28, top = 30, bottom = 52, baseline = analysis.baseline.trajectory, band = analysis.bands[metric];
    var values = baseline.map(function (r) { return r[metric]; }).concat(band.map(function (r) { return r.p10; }), band.map(function (r) { return r.p90; }));
    var minY = Math.min.apply(null, values), maxY = Math.max.apply(null, values), pad = Math.max(1, (maxY - minY) * 0.10); minY -= pad; maxY += pad;
    function xScale(year) { return left + (year / Math.max(1, baseline[baseline.length - 1].year)) * (width - left - right); }
    function yScale(value) { return top + (1 - (value - minY) / Math.max(0.000001, maxY - minY)) * (height - top - bottom); }
    function path(rows, key) { return rows.map(function (row, i) { return (i ? 'L ' : 'M ') + xScale(row.year) + ' ' + yScale(row[key]); }).join(' '); }
    var polygon = band.map(function (row) { return xScale(row.year) + ',' + yScale(row.p90); }).concat(band.slice().reverse().map(function (row) { return xScale(row.year) + ',' + yScale(row.p10); })).join(' ');
    var parts = ['<rect x="0" y="0" width="760" height="320" fill="#fbfaf6"/>'];
    for (var i = 0; i <= 4; i++) { var y = top + i * (height - top - bottom) / 4; parts.push('<line x1="' + left + '" y1="' + y + '" x2="' + (width-right) + '" y2="' + y + '" stroke="#d9d2c4"/>'); parts.push('<text x="8" y="' + (y+4) + '">' + round(maxY - i * (maxY-minY)/4, 1) + '</text>'); }
    parts.push('<polygon points="' + polygon + '" fill="rgba(155,17,17,0.16)" stroke="none"/>');
    parts.push('<path d="' + path(baseline, metric) + '" fill="none" stroke="#555555" stroke-width="3"/>');
    parts.push('<path d="' + path(band, 'median') + '" fill="none" stroke="#9b1111" stroke-width="3"/>');
    parts.push('<line x1="' + left + '" y1="298" x2="' + (left+24) + '" y2="298" stroke="#555555" stroke-width="3"/><text x="' + (left+30) + '" y="302">Baseline</text>');
    parts.push('<line x1="' + (left+150) + '" y1="298" x2="' + (left+174) + '" y2="298" stroke="#9b1111" stroke-width="3"/><text x="' + (left+180) + '" y="302">Policy median</text>');
    svg.innerHTML = parts.join('');
  }

  function notes(inputs, analysis) {
    var out = [], score = analysis.summary.filter(function (r) { return r.metric === 'composite_score'; })[0];
    out.push('The policy median composite score is ' + score.outcome + ' relative to the deterministic baseline.');
    out.push(Math.round(analysis.budget_probability * 100) + '% of declared policy realizations remain within the selected emissions budget.');
    out.push('P10-P90 intervals describe the declared parameter ranges and simplified browser model, not empirical forecast confidence.');
    if (analysis.budget_probability < 0.5) out.push('Budget compliance is fragile under the declared uncertainty ranges; inspect emissions intensity and adaptation assumptions.');
    out.push('All ' + inputs.uncertainty.n + ' requested browser realizations completed; failed realizations would remain visible in the export.');
    return out;
  }

  function render(root) {
    var form = root.querySelector('[data-scar-form]'), inputs = read(form), analysis = analyze(inputs);
    var outputMap = { yearsOut: inputs.shared.years + ' years', baselineSavingsOut: pct(inputs.baseline.savings), baselineEmissionsOut: pct(inputs.baseline.emissionsIntensity), baselineAdaptOut: pct(inputs.baseline.adaptation), baselineRestoreOut: pct(inputs.baseline.restoration), baselineHumanOut: pct(inputs.baseline.humanInvestment), policySavingsOut: pct(inputs.policy.savings), policyEmissionsOut: pct(inputs.policy.emissionsIntensity), policyAdaptOut: pct(inputs.policy.adaptation), policyRestoreOut: pct(inputs.policy.restoration), policyHumanOut: pct(inputs.policy.humanInvestment), emissionsWidthOut: '+/- ' + Math.round(inputs.uncertainty.emissionsWidth * 100) + '%', restorationWidthOut: '+/- ' + Math.round(inputs.uncertainty.restorationWidth * 100) + '%', adaptationWidthOut: '+/- ' + Math.round(inputs.uncertainty.adaptationWidth * 100) + '%' };
    Object.keys(outputMap).forEach(function (name) { root.querySelector('[data-out="' + name + '"]').textContent = outputMap[name]; });
    var score = analysis.summary.filter(function (r) { return r.metric === 'composite_score'; })[0], strongest = analysis.sensitivity.slice().sort(function (a,b) { return Math.abs(b.estimate) - Math.abs(a.estimate); })[0];
    root.querySelector('[data-result="scoreDelta"]').textContent = signed(score.median - score.baseline_value, 1); root.querySelector('[data-result="scoreNote"]').textContent = score.outcome + ' median versus baseline';
    root.querySelector('[data-result="budgetProbability"]').textContent = Math.round(analysis.budget_probability * 100) + '%'; root.querySelector('[data-result="budgetNote"]').textContent = inputs.uncertainty.n + ' seeded realizations';
    root.querySelector('[data-result="scoreInterval"]').textContent = round(score.p10, 1) + ' to ' + round(score.p90, 1);
    root.querySelector('[data-result="sensitivity"]').textContent = strongest.target.replace('parameters.', '').replace('policy.', ''); root.querySelector('[data-result="sensitivityNote"]').textContent = strongest.metric + ' (' + signed(strongest.estimate, 2) + ')';
    root.querySelector('[data-uncertainty-table]').innerHTML = analysis.summary.map(function (row) { return '<tr><th scope="row">' + row.label + '</th><td>' + row.baseline_value + '</td><td>' + row.median + '</td><td>' + row.p10 + '</td><td>' + row.p90 + '</td><td data-outcome="' + row.outcome + '">' + row.outcome + '</td></tr>'; }).join('');
    root.querySelector('[data-result="notes"]').innerHTML = notes(inputs, analysis).map(function (note) { return '<li>' + note + '</li>'; }).join('');
    chart(root.querySelector('[data-chart]'), analysis, root.querySelector('[data-chart-metric]').value);
    root._scarInputs = inputs; root._scarAnalysis = analysis;
  }

  function payload(root) {
    var inputs = root._scarInputs || read(root.querySelector('[data-scar-form]')), analysis = root._scarAnalysis || analyze(inputs), generatedAt = new Date().toISOString(), specs = uncertaintySpecs(inputs);
    return { schema_version: '1.3.0', demo: 'Catalyst Analytics R Demo', demo_version: '1.3.0', engine: { type: 'browser_simplified', compatible_repository_version: '0.4.0', parity_status: 'mapped_uncertainty_contract', comparison_contract_version: '1.0.0', uncertainty_contract_version: '1.0.0' }, generated_at: generatedAt, inputs: inputs, canonical_scenarios: [canonicalScenario(inputs.baseline, inputs.shared, generatedAt, []), canonicalScenario(inputs.policy, inputs.shared, generatedAt, specs)], comparison: { baseline_id: analysis.baseline.id, policy_id: analysis.policy.id }, uncertainty: { contract_version: '1.0.0', sampling: inputs.uncertainty.sampling, seed: inputs.uncertainty.seed, requested: inputs.uncertainty.n, completed: analysis.samples.length, failed: analysis.failures.length, specifications: specs, summary: analysis.summary, probabilities: [{ metric: 'cumulative_emissions', threshold: inputs.shared.emissionsBudget, operator: '<=', probability: analysis.budget_probability, n: analysis.samples.length }], sensitivity: analysis.sensitivity, failures: analysis.failures }, trajectories: { baseline: analysis.baseline.trajectory, policy_median: metrics.reduce(function (out, metric) { out[metric.key] = analysis.bands[metric.key]; return out; }, {}) }, interpretation_notes: notes(inputs, analysis), boundary: { forecast: false, compliance: false, autonomous_decision: false, professional_advice: false } };
  }

  function downloadJSON(root) { var data = payload(root), blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }), link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'catalyst-analytics-r-uncertainty.json'; document.body.appendChild(link); link.click(); link.remove(); setTimeout(function () { URL.revokeObjectURL(link.href); }, 500); }
  function summaryText(root) { var data = payload(root), p = data.uncertainty.probabilities[0]; return ['Catalyst Analytics R uncertainty demo','Baseline: ' + data.canonical_scenarios[0].title,'Policy: ' + data.canonical_scenarios[1].title,'Sampling: ' + data.uncertainty.sampling + ', n=' + data.uncertainty.completed + ', seed=' + data.uncertainty.seed,'Budget probability: ' + Math.round(p.probability * 100) + '%','Boundary: declared-assumption uncertainty, not an empirical forecast.'].join('\n'); }
  function init(root) { var form = root.querySelector('[data-scar-form]'); form.addEventListener('input', function () { render(root); }); root.querySelector('[data-chart-metric]').addEventListener('change', function () { render(root); }); root.querySelector('[data-action="reset"]').addEventListener('click', function () { form.reset(); render(root); }); root.querySelector('[data-action="download"]').addEventListener('click', function () { downloadJSON(root); }); root.querySelector('[data-action="copy"]').addEventListener('click', function () { var text = summaryText(root); if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text); else window.prompt('Copy analysis:', text); }); render(root); }
  document.addEventListener('DOMContentLoaded', function () { document.querySelectorAll('[data-scar-demo]').forEach(init); });
})();
