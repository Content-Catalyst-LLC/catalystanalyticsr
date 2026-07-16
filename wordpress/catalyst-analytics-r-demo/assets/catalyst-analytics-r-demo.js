(function () {
  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function pct(n) {
    return Math.round(n * 100) + '%';
  }

  function round(n, digits) {
    var m = Math.pow(10, digits || 1);
    return Math.round(n * m) / m;
  }

  function read(form) {
    var fd = new FormData(form);
    return {
      scenarioName: String(fd.get('scenarioName') || 'Policy pathway'),
      years: Number(fd.get('years') || 20),
      savings: Number(fd.get('savings') || 22) / 100,
      emissionsIntensity: Number(fd.get('emissionsIntensity') || 7) / 100,
      adaptation: Number(fd.get('adaptation') || 8) / 100,
      restoration: Number(fd.get('restoration') || 6) / 100,
      humanInvestment: Number(fd.get('humanInvestment') || 5) / 100,
      initialCapital: Number(fd.get('initialCapital') || 100),
      initialHuman: Number(fd.get('initialHuman') || 100),
      initialNatural: Number(fd.get('initialNatural') || 100),
      emissionsBudget: Number(fd.get('emissionsBudget') || 120)
    };
  }

  function simulate(x) {
    var rows = [];
    var K = x.initialCapital;
    var H = x.initialHuman;
    var N = x.initialNatural;
    var C = 0;
    var baseProductivity = 0.030;
    var depreciation = 0.018;
    var naturalDrag = 0.010;
    var adaptationProtection = 0.018 * x.adaptation;
    for (var t = 0; t <= x.years; t++) {
      var output = 0.42 * K + 0.34 * H + 0.24 * N;
      var emissions = output * x.emissionsIntensity * (1 - 0.55 * x.adaptation);
      var depletion = Math.max(0, emissions * 0.30 - x.restoration * 8);
      var ans = (x.savings * output) + (x.humanInvestment * output * 0.35) + (x.restoration * output * 0.25) - depletion - emissions * 0.15;
      var composite = (0.38 * K + 0.32 * H + 0.30 * N) - (0.18 * C);
      rows.push({
        year: t,
        produced_capital: round(K, 2),
        human_capital: round(H, 2),
        natural_capital: round(N, 2),
        cumulative_emissions: round(C, 2),
        adjusted_savings: round(ans, 2),
        composite_score: round(composite, 2)
      });
      C += emissions;
      K += (baseProductivity + x.savings * 0.09) * K - depreciation * K;
      H += (0.012 + x.humanInvestment * 0.12) * H;
      N += x.restoration * 4 + adaptationProtection * 30 - naturalDrag * emissions - depletion * 0.05;
      N = Math.max(1, N);
    }
    var finalRow = rows[rows.length - 1];
    var start = rows[0];
    var budgetRatio = finalRow.cumulative_emissions / Math.max(1, x.emissionsBudget);
    var naturalChange = (finalRow.natural_capital - start.natural_capital) / Math.max(1, start.natural_capital);
    var capitalChange = (finalRow.produced_capital - start.produced_capital) / Math.max(1, start.produced_capital);
    var humanChange = (finalRow.human_capital - start.human_capital) / Math.max(1, start.human_capital);
    var score = clamp(50 + capitalChange * 18 + humanChange * 16 + naturalChange * 22 - Math.max(0, budgetRatio - 1) * 35, 0, 100);
    return { inputs: x, trajectory: rows, final: finalRow, budgetRatio: budgetRatio, score: round(score, 1) };
  }

  function noteList(run) {
    var notes = [];
    var f = run.final;
    if (run.budgetRatio <= 0.8) notes.push('Cumulative emissions remain comfortably below the selected budget in this simplified run.');
    else if (run.budgetRatio <= 1) notes.push('Cumulative emissions remain within the selected budget, but the margin is narrow.');
    else notes.push('Cumulative emissions exceed the selected budget; review emissions intensity, adaptation, or horizon assumptions.');
    if (f.adjusted_savings > 0) notes.push('Final-period adjusted savings are positive, suggesting reinvestment outweighs modeled depletion and emissions penalties.');
    else notes.push('Final-period adjusted savings are negative; the scenario may be drawing down capital faster than it rebuilds it.');
    if (f.natural_capital >= run.trajectory[0].natural_capital) notes.push('Natural capital is preserved or improved in this simplified trajectory.');
    else notes.push('Natural capital declines over the horizon; review restoration, depletion, and emissions assumptions.');
    notes.push('Treat this as an exploratory demo, not a forecast or professional analysis.');
    return notes;
  }

  function chart(svg, run) {
    var rows = run.trajectory;
    var width = 720, height = 300, left = 55, right = 25, top = 28, bottom = 46;
    var keys = ['produced_capital', 'human_capital', 'natural_capital', 'cumulative_emissions'];
    var labels = ['Produced capital', 'Human capital', 'Natural capital', 'Cumulative emissions'];
    var colors = ['#000000', '#555555', '#9b1111', '#8a6a3f'];
    var maxY = Math.max.apply(null, rows.flatMap(function (r) { return keys.map(function (k) { return r[k]; }); }));
    maxY = Math.max(10, maxY * 1.08);
    function xScale(t) { return left + (t / run.inputs.years) * (width - left - right); }
    function yScale(v) { return top + (1 - v / maxY) * (height - top - bottom); }
    function pathFor(k) {
      return rows.map(function (r, i) {
        return (i === 0 ? 'M ' : 'L ') + xScale(r.year) + ' ' + yScale(r[k]);
      }).join(' ');
    }
    var parts = [];
    parts.push('<rect x="0" y="0" width="720" height="300" fill="#fbfaf6"/>');
    for (var i = 0; i <= 4; i++) {
      var y = top + i * (height - top - bottom) / 4;
      parts.push('<line x1="' + left + '" y1="' + y + '" x2="' + (width - right) + '" y2="' + y + '" stroke="#d9d2c4" stroke-width="1"/>');
      parts.push('<text x="12" y="' + (y + 4) + '">' + round(maxY * (1 - i/4), 0) + '</text>');
    }
    parts.push('<line x1="' + left + '" y1="' + (height-bottom) + '" x2="' + (width-right) + '" y2="' + (height-bottom) + '" stroke="#000"/>');
    parts.push('<line x1="' + left + '" y1="' + top + '" x2="' + left + '" y2="' + (height-bottom) + '" stroke="#000"/>');
    keys.forEach(function (k, idx) {
      parts.push('<path d="' + pathFor(k) + '" fill="none" stroke="' + colors[idx] + '" stroke-width="3" stroke-linecap="round"/>');
    });
    keys.forEach(function (k, idx) {
      var y = height - 22;
      var x = left + idx * 158;
      parts.push('<rect x="' + x + '" y="' + (y-10) + '" width="12" height="3" fill="' + colors[idx] + '"/>');
      parts.push('<text x="' + (x+17) + '" y="' + y + '">' + labels[idx] + '</text>');
    });
    parts.push('<text x="' + left + '" y="286">0</text><text x="' + (width-right-35) + '" y="286">year ' + run.inputs.years + '</text>');
    svg.innerHTML = parts.join('');
  }

  function render(root) {
    var form = root.querySelector('[data-scar-form]');
    var inputs = read(form);
    var run = simulate(inputs);
    root.querySelector('[data-out="yearsOut"]').textContent = inputs.years + ' years';
    root.querySelector('[data-out="savingsOut"]').textContent = pct(inputs.savings);
    root.querySelector('[data-out="emissionsOut"]').textContent = pct(inputs.emissionsIntensity);
    root.querySelector('[data-out="adaptOut"]').textContent = pct(inputs.adaptation);
    root.querySelector('[data-out="restoreOut"]').textContent = pct(inputs.restoration);
    root.querySelector('[data-out="humanOut"]').textContent = pct(inputs.humanInvestment);
    root.querySelector('[data-result="score"]').textContent = run.score + '/100';
    root.querySelector('[data-result="scoreNote"]').textContent = run.score >= 70 ? 'stronger pathway' : run.score >= 50 ? 'mixed pathway' : 'high-risk pathway';
    root.querySelector('[data-result="ans"]').textContent = String(run.final.adjusted_savings);
    var budgetText = run.budgetRatio <= 1 ? 'Within budget' : 'Over budget';
    root.querySelector('[data-result="budget"]').textContent = budgetText;
    root.querySelector('[data-result="budgetNote"]').textContent = round(run.final.cumulative_emissions, 1) + ' / ' + inputs.emissionsBudget;
    var notes = root.querySelector('[data-result="notes"]');
    notes.innerHTML = noteList(run).map(function (n) { return '<li>' + n + '</li>'; }).join('');
    chart(root.querySelector('[data-chart]'), run);
    root._scarRun = run;
  }

  function summary(run) {
    return [
      'Catalyst Analytics R demo summary',
      'Scenario: ' + run.inputs.scenarioName,
      'Horizon: ' + run.inputs.years + ' years',
      'Composite score: ' + run.score + '/100',
      'Final adjusted savings: ' + run.final.adjusted_savings,
      'Cumulative emissions: ' + run.final.cumulative_emissions + ' / budget ' + run.inputs.emissionsBudget,
      'Budget status: ' + (run.budgetRatio <= 1 ? 'within budget' : 'over budget'),
      'Note: exploratory browser demo, not a forecast or professional advice.'
    ].join('\n');
  }

  function downloadJSON(root) {
    var run = root._scarRun || simulate(read(root.querySelector('[data-scar-form]')));
    var payload = {
      schema_version: '1.0.0',
      demo: 'Catalyst Analytics R Demo',
      demo_version: '1.0.1',
      engine: {
        type: 'browser_simplified',
        compatible_repository_version: '0.1.4',
        parity_status: 'conceptual_only'
      },
      generated_at: new Date().toISOString(),
      inputs: run.inputs,
      final: run.final,
      composite_score: run.score,
      budget_ratio: round(run.budgetRatio, 3),
      interpretation_notes: noteList(run),
      trajectory: run.trajectory,
      boundary: { forecast: false, compliance: false, professional_advice: false }
    };
    var blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'catalyst-analytics-r-demo-export.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 500);
  }

  function init(root) {
    var form = root.querySelector('[data-scar-form]');
    form.addEventListener('input', function () { render(root); });
    root.querySelector('[data-action="reset"]').addEventListener('click', function () { form.reset(); render(root); });
    root.querySelector('[data-action="download"]').addEventListener('click', function () { downloadJSON(root); });
    root.querySelector('[data-action="copy"]').addEventListener('click', function () {
      var text = summary(root._scarRun || simulate(read(form)));
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text);
      else window.prompt('Copy summary:', text);
    });
    render(root);
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-scar-demo]').forEach(init);
  });
})();
