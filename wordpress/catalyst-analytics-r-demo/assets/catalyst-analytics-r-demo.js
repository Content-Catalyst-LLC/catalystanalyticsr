(function () {
  'use strict';

  var CONTRACT = {
    parity_status: 'mapped_inclusive_development_contract',
    compatible_repository_version: '0.7.0',
    wealth_contract_version: '1.0.0',
    human_development_contract_version: '1.0.0',
    distribution_contract_version: '1.0.0',
    composite_score_contract_version: '1.0.0',
    inclusive_development_contract_version: '1.0.0'
  };

  function number(form, name) {
    var value = Number(form.elements[name].value);
    if (!Number.isFinite(value)) throw new Error('Enter a valid value for ' + name + '.');
    return value;
  }
  function clamp(value) { return Math.max(0, Math.min(1, value)); }
  function format(value, digits) { return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits == null ? 2 : digits }); }
  function parseQuintiles(value) {
    var values = String(value).split(',').map(function (entry) { return Number(entry.trim()); });
    if (values.length !== 5 || values.some(function (entry) { return !Number.isFinite(entry) || entry < 0; })) throw new Error('Enter five non-negative quintile values separated by commas.');
    return values;
  }
  function weightedGini(values) {
    var ordered = values.slice().sort(function (a, b) { return a - b; });
    var total = ordered.reduce(function (sum, value) { return sum + value; }, 0);
    if (total === 0) return 0;
    var weighted = ordered.reduce(function (sum, value, index) { return sum + (index + 1) * value; }, 0);
    return (2 * weighted) / (ordered.length * total) - (ordered.length + 1) / ordered.length;
  }
  function normalized(value, lower, upper, direction) {
    var score = clamp((value - lower) / (upper - lower));
    return direction === 'lower' ? 1 - score : score;
  }
  function normalizeWeights(raw) {
    var total = Object.keys(raw).reduce(function (sum, key) { return sum + raw[key]; }, 0);
    if (total <= 0) throw new Error('At least one composite weight must be positive.');
    var result = {};
    Object.keys(raw).forEach(function (key) { result[key] = raw[key] / total; });
    return result;
  }
  function scoreWithWeights(componentScores, weights) {
    return 100 * Object.keys(componentScores).reduce(function (sum, key) { return sum + componentScores[key] * weights[key]; }, 0);
  }
  function weightSensitivity(componentScores, weights) {
    var rows = [];
    Object.keys(weights).forEach(function (target) {
      [-0.2, 0.2].forEach(function (shift) {
        var changed = Object.assign({}, weights);
        var newTarget = Math.max(0, Math.min(1, weights[target] * (1 + shift)));
        var remainingOld = 1 - weights[target];
        changed[target] = newTarget;
        Object.keys(changed).forEach(function (key) {
          if (key !== target) changed[key] = remainingOld > 0 ? weights[key] * (1 - newTarget) / remainingOld : 0;
        });
        rows.push({ component: target, perturbation: shift < 0 ? 'decrease' : 'increase', original_weight: weights[target], perturbed_weight: newTarget, score: scoreWithWeights(componentScores, changed) });
      });
    });
    return rows;
  }

  function buildAnalysis(form) {
    var inputs = {
      entity: form.elements.entity.value.trim() || 'Untitled entity',
      start_year: number(form, 'startYear'), end_year: number(form, 'endYear'),
      population_start: number(form, 'populationStart'), population_end: number(form, 'populationEnd'),
      produced_opening: number(form, 'producedOpening'), produced_closing: number(form, 'producedClosing'), produced_shadow_price: number(form, 'producedPrice'),
      human_opening: number(form, 'humanOpening'), human_closing: number(form, 'humanClosing'), human_shadow_price: number(form, 'humanPrice'),
      natural_opening: number(form, 'naturalOpening'), natural_closing: number(form, 'naturalClosing'), natural_shadow_price: number(form, 'naturalPrice'),
      gross_savings: number(form, 'grossSavings'), gni: number(form, 'gni'), depreciation: number(form, 'depreciation'), education_investment: number(form, 'education'), health_investment: number(form, 'health'), resource_depletion: number(form, 'depletion'), pollution_damages: number(form, 'pollution'), climate_damages: number(form, 'climate'),
      life_expectancy: number(form, 'life'), income_per_capita: number(form, 'income'), expected_schooling: number(form, 'expectedSchool'), mean_schooling: number(form, 'meanSchool'),
      social_floor: number(form, 'socialFloor'), quintile_values: parseQuintiles(form.elements.quintiles.value),
      component_weights: normalizeWeights({ wealth_per_capita: number(form, 'wealthWeight'), adjusted_savings_rate: number(form, 'savingsWeight'), human_development: number(form, 'humanWeight'), natural_share: number(form, 'naturalWeight') })
    };
    if (inputs.end_year <= inputs.start_year) throw new Error('End year must be later than start year.');
    if (inputs.population_start <= 0 || inputs.population_end <= 0 || inputs.gni <= 0) throw new Error('Population and GNI must be positive.');
    ['produced_opening','produced_closing','human_opening','human_closing','natural_opening','natural_closing'].forEach(function (key) { if (inputs[key] < 0) throw new Error('Capital stocks cannot be negative.'); });
    ['produced_shadow_price','human_shadow_price','natural_shadow_price'].forEach(function (key) { if (inputs[key] <= 0) throw new Error('Shadow prices must be positive.'); });

    var capitalAccounts = {
      produced: { opening_value: inputs.produced_opening * inputs.produced_shadow_price, closing_value: inputs.produced_closing * inputs.produced_shadow_price },
      human: { opening_value: inputs.human_opening * inputs.human_shadow_price, closing_value: inputs.human_closing * inputs.human_shadow_price },
      natural: { opening_value: inputs.natural_opening * inputs.natural_shadow_price, closing_value: inputs.natural_closing * inputs.natural_shadow_price }
    };
    Object.keys(capitalAccounts).forEach(function (key) { capitalAccounts[key].change = capitalAccounts[key].closing_value - capitalAccounts[key].opening_value; });
    var openingWealth = Object.keys(capitalAccounts).reduce(function (sum, key) { return sum + capitalAccounts[key].opening_value; }, 0);
    var closingWealth = Object.keys(capitalAccounts).reduce(function (sum, key) { return sum + capitalAccounts[key].closing_value; }, 0);
    var inclusiveWealth = {
      opening: openingWealth, closing: closingWealth, change: closingWealth - openingWealth,
      per_capita_opening: openingWealth / inputs.population_start,
      per_capita_closing: closingWealth / inputs.population_end,
      produced_share: capitalAccounts.produced.closing_value / closingWealth,
      human_share: capitalAccounts.human.closing_value / closingWealth,
      natural_share: capitalAccounts.natural.closing_value / closingWealth
    };

    var humanInvestment = inputs.education_investment + inputs.health_investment;
    var totalDeductions = inputs.depreciation + inputs.resource_depletion + inputs.pollution_damages + inputs.climate_damages;
    var adjusted = inputs.gross_savings + humanInvestment - totalDeductions;
    var ans = { gross_savings: inputs.gross_savings, produced_capital_depreciation: inputs.depreciation, education_investment: inputs.education_investment, health_investment: inputs.health_investment, human_capital_investment: humanInvestment, natural_resource_depletion: inputs.resource_depletion, pollution_damages: inputs.pollution_damages, climate_damages: inputs.climate_damages, total_deductions: totalDeductions, adjusted_net_savings: adjusted, gni: inputs.gni, adjusted_net_savings_percent_gni: 100 * adjusted / inputs.gni, sustainable_savings_signal: adjusted >= 0 };

    var lifeIndex = clamp((inputs.life_expectancy - 20) / 65);
    var educationIndex = (clamp(inputs.expected_schooling / 18) + clamp(inputs.mean_schooling / 15)) / 2;
    var incomeIndex = clamp((Math.log(Math.max(inputs.income_per_capita, 100)) - Math.log(100)) / (Math.log(75000) - Math.log(100)));
    var hdi = { life_expectancy_index: lifeIndex, education_index: educationIndex, income_index: incomeIndex, human_development_index: Math.pow(lifeIndex * educationIndex * incomeIndex, 1 / 3) };

    var ordered = inputs.quintile_values.slice().sort(function (a, b) { return a - b; });
    var total = ordered.reduce(function (sum, value) { return sum + value; }, 0);
    var groupSummary = ordered.map(function (value, index) { return { group: 'Quintile ' + (index + 1), observations: 1, weight: 0.2, weighted_mean: value, resource_share: total === 0 ? 0 : value / total, population_share: 0.2 }; });
    var distribution = { schema_version: '1.0.0', analysis_type: 'distributional', indicator: 'household_resources', unit: 'resource_index', entity: inputs.entity, time: inputs.end_year, higher_is_better: true, summary: { observations: 5, total_weight: 1, weighted_mean: total / 5, weighted_median: ordered[2], p10: ordered[0], p40: ordered[1], p90: ordered[4], p90_p10_ratio: ordered[0] === 0 ? null : ordered[4] / ordered[0], gini: weightedGini(ordered), top_10_share: total === 0 ? 0 : ordered[4] / total, bottom_40_share: total === 0 ? 0 : (ordered[0] + ordered[1]) / total, palma_ratio: ordered[0] + ordered[1] === 0 ? null : ordered[4] / (ordered[0] + ordered[1]), social_floor: inputs.social_floor, share_below_social_floor: ordered.filter(function (value) { return value < inputs.social_floor; }).length / 5 }, group_summary: groupSummary, records: groupSummary.map(function (row) { return { value: row.weighted_mean, weight: row.weight, group: row.group }; }), meta: { created_at: new Date().toISOString(), interpretation: 'lower-tail shortfalls require review' } };

    var componentScores = { wealth_per_capita: normalized(inclusiveWealth.per_capita_closing, 250, 350, 'higher'), adjusted_savings_rate: normalized(ans.adjusted_net_savings_percent_gni, -5, 15, 'higher'), human_development: normalized(hdi.human_development_index, 0.55, 0.9, 'higher'), natural_share: normalized(inclusiveWealth.natural_share, 0.15, 0.35, 'higher') };
    var definitionComponents = [
      { component: 'wealth_per_capita', weight: inputs.component_weights.wealth_per_capita, direction: 'higher', lower_bound: 250, upper_bound: 350 },
      { component: 'adjusted_savings_rate', weight: inputs.component_weights.adjusted_savings_rate, direction: 'higher', lower_bound: -5, upper_bound: 15 },
      { component: 'human_development', weight: inputs.component_weights.human_development, direction: 'higher', lower_bound: 0.55, upper_bound: 0.9 },
      { component: 'natural_share', weight: inputs.component_weights.natural_share, direction: 'higher', lower_bound: 0.15, upper_bound: 0.35 }
    ];
    var componentRows = definitionComponents.map(function (spec) { return Object.assign({}, spec, { raw_value: spec.component === 'wealth_per_capita' ? inclusiveWealth.per_capita_closing : spec.component === 'adjusted_savings_rate' ? ans.adjusted_net_savings_percent_gni : spec.component === 'human_development' ? hdi.human_development_index : inclusiveWealth.natural_share, normalized_score: componentScores[spec.component], weighted_contribution: 100 * componentScores[spec.component] * spec.weight }); });
    var composite = { definition: { schema_version: '1.0.0', id: 'browser-inclusive-development-score', title: 'Browser inclusive development score', components: definitionComponents, missing_policy: 'error', meta: { normalization: 'bounded_min_max', score_range: [0, 100] } }, score: scoreWithWeights(componentScores, inputs.component_weights), component_scores: componentRows, weight_sensitivity: weightSensitivity(componentScores, inputs.component_weights) };
    var intergenerational = { start_per_capita: inclusiveWealth.per_capita_opening, end_per_capita: inclusiveWealth.per_capita_closing, change: inclusiveWealth.per_capita_closing - inclusiveWealth.per_capita_opening, non_declining_signal: inclusiveWealth.per_capita_closing >= inclusiveWealth.per_capita_opening };

    return { schema_version: '1.6.0', export_type: 'browser_inclusive_development', demo_version: '1.6.0', generated_at: new Date().toISOString(), contract: CONTRACT, inputs: inputs, capital_accounts: capitalAccounts, inclusive_wealth: inclusiveWealth, adjusted_net_savings: ans, human_development: hdi, distribution: distribution, intergenerational: intergenerational, composite: composite, review_boundary: { shadow_prices_require_review: true, human_capital_measurement_requires_review: true, social_floor_requires_review: true, distribution_weights_require_review: true, composite_weights_require_review: true, not_compliance_or_professional_advice: true } };
  }

  function drawChart(canvas, analysis) {
    var ratio = window.devicePixelRatio || 1, width = Math.max(520, Math.round(canvas.getBoundingClientRect().width || 760)), height = 280;
    canvas.width = width * ratio; canvas.height = height * ratio;
    var ctx = canvas.getContext('2d'); ctx.scale(ratio, ratio); ctx.clearRect(0, 0, width, height);
    var types = ['produced','human','natural'], labels = ['Produced','Human','Natural'];
    var values = types.reduce(function (all, key) { all.push(analysis.capital_accounts[key].opening_value, analysis.capital_accounts[key].closing_value); return all; }, [0]);
    var max = Math.max.apply(null, values) * 1.12, base = height - 42, chartHeight = height - 72, groupWidth = (width - 80) / types.length;
    ctx.strokeStyle = '#d9d5cf'; ctx.beginPath(); ctx.moveTo(52, base); ctx.lineTo(width - 20, base); ctx.stroke();
    types.forEach(function (key, i) {
      var x = 60 + i * groupWidth, opening = analysis.capital_accounts[key].opening_value, closing = analysis.capital_accounts[key].closing_value;
      var openHeight = chartHeight * opening / max, closeHeight = chartHeight * closing / max;
      ctx.fillStyle = '#d7d3cd'; ctx.fillRect(x, base - openHeight, groupWidth * 0.28, openHeight);
      ctx.fillStyle = '#701f2b'; ctx.fillRect(x + groupWidth * 0.34, base - closeHeight, groupWidth * 0.28, closeHeight);
      ctx.fillStyle = '#111'; ctx.font = '11px Montserrat, Arial'; ctx.textAlign = 'center'; ctx.fillText(labels[i], x + groupWidth * 0.31, base + 18);
      ctx.fillText(format(closing, 0), x + groupWidth * 0.48, base - closeHeight - 7);
    });
    ctx.textAlign = 'left'; ctx.fillStyle = '#5f5b56'; ctx.fillText('Opening', 52, 16); ctx.fillStyle = '#701f2b'; ctx.fillText('Closing', 115, 16);
  }

  function render(root, analysis) {
    root.querySelector('[data-scar-wealth]').textContent = format(analysis.inclusive_wealth.closing, 1);
    root.querySelector('[data-scar-per-capita]').textContent = format(analysis.inclusive_wealth.per_capita_closing, 1);
    root.querySelector('[data-scar-ans]').textContent = format(analysis.adjusted_net_savings.adjusted_net_savings_percent_gni, 2) + '%';
    root.querySelector('[data-scar-score]').textContent = format(analysis.composite.score, 1);
    var generation = root.querySelector('[data-scar-generation]'); generation.textContent = analysis.intergenerational.non_declining_signal ? 'Non-declining' : 'Declining'; generation.dataset.state = analysis.intergenerational.non_declining_signal ? 'within' : 'breached';
    drawChart(root.querySelector('[data-scar-chart]'), analysis);
    root.querySelector('[data-scar-composition]').innerHTML = ['produced','human','natural'].map(function (key) { return '<article><span>' + key + '</span><strong>' + format(100 * analysis.inclusive_wealth[key + '_share'], 1) + '%</strong></article>'; }).join('');
    var ans = analysis.adjusted_net_savings;
    root.querySelector('[data-scar-ans-ledger]').innerHTML = [
      ['Gross savings', ans.gross_savings, 'add'], ['Education + health', ans.human_capital_investment, 'add'], ['Depreciation', -ans.produced_capital_depreciation, 'subtract'], ['Resource depletion', -ans.natural_resource_depletion, 'subtract'], ['Pollution + climate', -(ans.pollution_damages + ans.climate_damages), 'subtract'], ['Adjusted Net Savings', ans.adjusted_net_savings, 'total']
    ].map(function (row) { return '<div data-kind="' + row[2] + '"><span>' + row[0] + '</span><strong>' + (row[1] > 0 && row[2] !== 'total' ? '+' : '') + format(row[1], 1) + '</strong></div>'; }).join('');
    var hdi = analysis.human_development;
    root.querySelector('[data-scar-hdi]').innerHTML = [['Life expectancy',hdi.life_expectancy_index],['Education',hdi.education_index],['Income',hdi.income_index],['Combined HDI',hdi.human_development_index]].map(function (row) { return '<article><span>' + row[0] + '</span><div><i style="width:' + (100 * row[1]) + '%"></i></div><strong>' + format(row[1], 3) + '</strong></article>'; }).join('');
    var floor = root.querySelector('[data-scar-floor]'); floor.textContent = format(100 * analysis.distribution.summary.share_below_social_floor, 0) + '% below floor'; floor.dataset.state = analysis.distribution.summary.share_below_social_floor > 0.2 ? 'breached' : analysis.distribution.summary.share_below_social_floor > 0 ? 'warning' : 'within';
    var maxValue = Math.max.apply(null, analysis.inputs.quintile_values.concat([1]));
    root.querySelector('[data-scar-distribution]').innerHTML = analysis.distribution.group_summary.map(function (row) { var below = row.weighted_mean < analysis.inputs.social_floor; return '<article data-state="' + (below ? 'below' : 'above') + '"><span>' + row.group + '</span><div><i style="width:' + (100 * row.weighted_mean / maxValue) + '%"></i></div><strong>' + format(row.weighted_mean, 1) + '</strong></article>'; }).join('');
    root.querySelector('[data-scar-distribution-metrics]').innerHTML = '<span>Gini <strong>' + format(analysis.distribution.summary.gini, 3) + '</strong></span><span>Palma <strong>' + format(analysis.distribution.summary.palma_ratio, 2) + '</strong></span><span>P90/P10 <strong>' + format(analysis.distribution.summary.p90_p10_ratio, 2) + '</strong></span>';
    var sensitivitySpread = Math.max.apply(null, analysis.composite.weight_sensitivity.map(function (row) { return Math.abs(row.score - analysis.composite.score); }));
    var sensitivity = root.querySelector('[data-scar-sensitivity]'); sensitivity.textContent = 'Max shift ' + format(sensitivitySpread, 1); sensitivity.dataset.state = sensitivitySpread > 8 ? 'breached' : sensitivitySpread > 4 ? 'warning' : 'within';
    root.querySelector('[data-scar-components]').innerHTML = analysis.composite.component_scores.map(function (row) { return '<article><div><span>' + row.component.replaceAll('_',' ') + '</span><small>Weight ' + format(100 * row.weight, 0) + '%</small></div><strong>' + format(row.weighted_contribution, 1) + '</strong><div class="scar-demo__component-bar"><i style="width:' + (100 * row.normalized_score) + '%"></i></div></article>'; }).join('');
  }

  function downloadJSON(data) {
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = 'catalyst-analytics-r-inclusive-development.json'; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url);
  }
  function init(root) {
    var form = root.querySelector('[data-scar-form]'), latest = null;
    function run(event) { if (event) event.preventDefault(); try { latest = buildAnalysis(form); render(root, latest); } catch (error) { window.alert(error.message); } }
    form.addEventListener('submit', run);
    root.querySelector('[data-scar-download]').addEventListener('click', function () { if (!latest) run(); if (latest) downloadJSON(latest); });
    root.querySelector('[data-scar-reset]').addEventListener('click', function () { form.reset(); run(); });
    window.addEventListener('resize', function () { if (latest) drawChart(root.querySelector('[data-scar-chart]'), latest); });
    run();
  }
  document.addEventListener('DOMContentLoaded', function () { document.querySelectorAll('[data-scar-demo]').forEach(init); });
}());
