(function () {
  'use strict';

  var CONTRACT = {
    compatible_repository_version: '0.6.0',
    browser_demo_version: '1.5.0',
    emissions_inventory_contract_version: '1.0.0',
    climate_accounting_contract_version: '1.0.0',
    natural_capital_contract_version: '1.0.0',
    boundary_contract_version: '1.0.0',
    parity_status: 'mapped_contract_browser_calculation'
  };

  function number(form, name) {
    var input = form.elements[name];
    var value = Number(input.value);
    if (!Number.isFinite(value)) throw new Error('Enter a valid value for ' + name + '.');
    return value;
  }

  function percent(form, name) {
    return number(form, name) / 100;
  }

  function format(value, digits) {
    if (!Number.isFinite(value)) return 'n/a';
    return value.toLocaleString(undefined, { maximumFractionDigits: digits == null ? 1 : digits });
  }

  function logarithmicMean(x, y) {
    if (!(x > 0) || !(y > 0)) return null;
    if (Math.abs(x - y) < 1e-12) return x;
    return (x - y) / (Math.log(x) - Math.log(y));
  }

  function statusAtOrBelow(value, upper, warningMargin) {
    var scale = Math.max(Math.abs(upper), 1);
    var distance = upper - value;
    var status = value > upper ? 'breached' : distance <= scale * warningMargin ? 'warning' : 'within';
    return { status: status, distance: distance, normalized_distance: distance / scale };
  }

  function statusAtOrAbove(value, lower, warningMargin) {
    var scale = Math.max(Math.abs(lower), 1);
    var distance = value - lower;
    var status = value < lower ? 'breached' : distance <= scale * warningMargin ? 'warning' : 'within';
    return { status: status, distance: distance, normalized_distance: distance / scale };
  }

  function buildAnalysis(form) {
    var startYear = Math.trunc(number(form, 'startYear'));
    var endYear = Math.trunc(number(form, 'endYear'));
    if (endYear <= startYear) throw new Error('End year must be after start year.');
    if (endYear - startYear > 100) throw new Error('The browser demonstration is limited to 100 annual periods.');

    var inputs = {
      start_year: startYear,
      end_year: endYear,
      carbon_budget: number(form, 'carbonBudget'),
      starting_emissions: number(form, 'startingEmissions'),
      annual_decarbonization_rate: percent(form, 'decarbonization'),
      starting_removals: number(form, 'startingRemovals'),
      annual_removals_growth_rate: percent(form, 'removalsGrowth'),
      target_net_emissions: number(form, 'targetNet'),
      gdp_growth_rate: percent(form, 'gdpGrowth'),
      population_growth_rate: percent(form, 'populationGrowth'),
      energy_intensity_improvement_rate: percent(form, 'energyIntensityImprovement'),
      natural_capital_opening: number(form, 'naturalOpening'),
      natural_capital_floor: number(form, 'naturalFloor'),
      annual_regeneration: number(form, 'regeneration'),
      annual_restoration: number(form, 'restoration'),
      annual_extraction: number(form, 'extraction'),
      annual_degradation: number(form, 'degradation'),
      annual_damages: number(form, 'damages')
    };

    if (inputs.carbon_budget < 0 || inputs.starting_emissions < 0 || inputs.starting_removals < 0 || inputs.natural_capital_opening < 0 || inputs.natural_capital_floor < 0) {
      throw new Error('Budgets, emissions, removals, and natural-capital stocks cannot be negative.');
    }
    if (inputs.annual_decarbonization_rate < 0 || inputs.annual_decarbonization_rate > 1) {
      throw new Error('Annual decarbonization must be between 0 and 100 percent.');
    }

    var inventory = [];
    var pathway = [];
    var natural = [];
    var cumulativeGross = 0;
    var cumulativeRemovals = 0;
    var opening = inputs.natural_capital_opening;

    for (var year = startYear; year <= endYear; year += 1) {
      var index = year - startYear;
      var gross = inputs.starting_emissions * Math.pow(1 - inputs.annual_decarbonization_rate, index);
      var removals = inputs.starting_removals * Math.pow(1 + inputs.annual_removals_growth_rate, index);
      var net = gross - removals;
      var population = 100 * Math.pow(1 + inputs.population_growth_rate, index);
      var gdp = 100 * Math.pow(1 + inputs.gdp_growth_rate, index);
      var energyIntensity = Math.pow(1 - inputs.energy_intensity_improvement_rate, index);
      var energy = gdp * energyIntensity;
      cumulativeGross += gross;
      cumulativeRemovals += removals;
      var cumulativeNet = cumulativeGross - cumulativeRemovals;
      var remaining = inputs.carbon_budget - cumulativeNet;

      inventory.push({
        region: 'Browser example', year: year, gross_emissions: gross, removals: removals,
        net_emissions: net, gas: 'CO2e', source_category: 'total', energy: energy,
        gdp: gdp, population: population
      });
      pathway.push({
        region: 'Browser example', year: year, gross_emissions: gross, removals: removals,
        net_emissions: net, cumulative_gross_emissions: cumulativeGross,
        cumulative_removals: cumulativeRemovals, cumulative_net_emissions: cumulativeNet,
        carbon_budget: inputs.carbon_budget, remaining_budget: remaining,
        budget_share_used: inputs.carbon_budget === 0 ? (cumulativeNet <= 0 ? 0 : null) : cumulativeNet / inputs.carbon_budget,
        within_budget: remaining >= 0, budget_status: remaining >= 0 ? 'within_budget' : 'overshoot'
      });

      var additions = inputs.annual_regeneration + inputs.annual_restoration;
      var losses = inputs.annual_extraction + inputs.annual_degradation + inputs.annual_damages;
      var closing = Math.max(0, opening + additions - losses);
      natural.push({
        entity: 'Browser example', time: year, opening_stock: opening,
        regeneration: inputs.annual_regeneration, restoration: inputs.annual_restoration,
        additions: 0, extraction: inputs.annual_extraction, degradation: inputs.annual_degradation,
        damages: inputs.annual_damages, expected_closing_stock: closing, closing_stock: closing,
        net_change: closing - opening, accounting_net_change: additions - losses,
        reconciliation_error: 0, unit: 'natural_capital_index'
      });
      opening = closing;
    }

    var first = inventory[0];
    var last = inventory[inventory.length - 1];
    var factors0 = {
      population: first.population,
      affluence: first.gdp / first.population,
      energy_intensity: first.energy / first.gdp,
      carbon_intensity: first.gross_emissions / first.energy
    };
    var factors1 = {
      population: last.population,
      affluence: last.gdp / last.population,
      energy_intensity: last.energy / last.gdp,
      carbon_intensity: last.gross_emissions / last.energy
    };
    var weight = logarithmicMean(last.gross_emissions, first.gross_emissions);
    var effects = {};
    Object.keys(factors0).forEach(function (key) {
      effects[key + '_effect'] = weight == null ? null : weight * Math.log(factors1[key] / factors0[key]);
    });
    var explained = Object.keys(effects).reduce(function (sum, key) { return sum + (effects[key] || 0); }, 0);
    var change = last.gross_emissions - first.gross_emissions;
    var kaya = {
      method: 'additive_lmdi_kaya_identity',
      contributions: [Object.assign({
        region: 'Browser example', baseline_time: startYear, comparison_time: endYear,
        baseline_emissions: first.gross_emissions, comparison_emissions: last.gross_emissions,
        emissions_change: change
      }, effects, { explained_change: explained, residual: change - explained, unit: 'emissions_index' })]
    };

    var cumulativeStatus = statusAtOrBelow(pathway[pathway.length - 1].cumulative_net_emissions, inputs.carbon_budget, 0.1);
    var terminalStatus = statusAtOrBelow(last.net_emissions, inputs.target_net_emissions, 0.1);
    var naturalStatus = statusAtOrAbove(natural[natural.length - 1].closing_stock, inputs.natural_capital_floor, 0.05);
    var assessments = [
      {
        indicator: 'cumulative_net_emissions', value: pathway[pathway.length - 1].cumulative_net_emissions,
        unit: 'emissions_index', boundary_id: 'declared-carbon-budget', boundary_title: 'Declared cumulative carbon budget',
        direction: 'at_or_below', lower: null, upper: inputs.carbon_budget, status: cumulativeStatus.status,
        distance: cumulativeStatus.distance, normalized_distance: cumulativeStatus.normalized_distance
      },
      {
        indicator: 'terminal_net_emissions', value: last.net_emissions,
        unit: 'emissions_index', boundary_id: 'target-net-emissions', boundary_title: 'Target net emissions',
        direction: 'at_or_below', lower: null, upper: inputs.target_net_emissions, status: terminalStatus.status,
        distance: terminalStatus.distance, normalized_distance: terminalStatus.normalized_distance
      },
      {
        indicator: 'natural_capital_closing_stock', value: natural[natural.length - 1].closing_stock,
        unit: 'natural_capital_index', boundary_id: 'natural-capital-floor', boundary_title: 'Natural-capital floor',
        direction: 'at_or_above', lower: inputs.natural_capital_floor, upper: null, status: naturalStatus.status,
        distance: naturalStatus.distance, normalized_distance: naturalStatus.normalized_distance
      }
    ];

    var overshoot = pathway.find(function (row) { return !row.within_budget; });
    return {
      schema_version: '1.5.0',
      export_type: 'browser_climate_accounting',
      demo_version: '1.5.0',
      generated_at: new Date().toISOString(),
      contract: CONTRACT,
      inputs: inputs,
      inventory: inventory,
      carbon_pathway: pathway,
      kaya_decomposition: kaya,
      natural_capital_account: natural,
      boundary_assessment: assessments,
      diagnostics: {
        cumulative_net_emissions: pathway[pathway.length - 1].cumulative_net_emissions,
        remaining_budget: pathway[pathway.length - 1].remaining_budget,
        overshoot_year: overshoot ? overshoot.year : null,
        terminal_net_emissions: last.net_emissions,
        natural_capital_closing_stock: natural[natural.length - 1].closing_stock,
        stranded_pathway_signal: Boolean(overshoot || last.net_emissions > inputs.target_net_emissions)
      },
      review_boundary: {
        educational_companion: true,
        source_review_required: true,
        budget_allocation_review_required: true,
        natural_capital_valuation_review_required: true,
        not_compliance_advice: true
      }
    };
  }

  function drawChart(canvas, pathway) {
    var rect = canvas.getBoundingClientRect();
    var ratio = window.devicePixelRatio || 1;
    var width = Math.max(520, Math.round(rect.width || 760));
    var height = 280;
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    var ctx = canvas.getContext('2d');
    ctx.scale(ratio, ratio);
    ctx.clearRect(0, 0, width, height);
    var pad = { left: 58, right: 20, top: 20, bottom: 42 };
    var values = pathway.reduce(function (all, row) {
      all.push(row.cumulative_net_emissions, row.carbon_budget);
      return all;
    }, [0]);
    var min = Math.min.apply(null, values);
    var max = Math.max.apply(null, values);
    if (max === min) max = min + 1;
    var x = function (i) { return pad.left + i * (width - pad.left - pad.right) / Math.max(1, pathway.length - 1); };
    var y = function (v) { return pad.top + (max - v) * (height - pad.top - pad.bottom) / (max - min); };

    ctx.strokeStyle = '#d9d5cf'; ctx.lineWidth = 1;
    for (var g = 0; g <= 4; g += 1) {
      var gy = pad.top + g * (height - pad.top - pad.bottom) / 4;
      ctx.beginPath(); ctx.moveTo(pad.left, gy); ctx.lineTo(width - pad.right, gy); ctx.stroke();
    }
    ctx.fillStyle = '#5f5b56'; ctx.font = '11px Montserrat, Arial';
    ctx.textAlign = 'right';
    for (var t = 0; t <= 4; t += 1) {
      var val = max - t * (max - min) / 4;
      ctx.fillText(format(val, 0), pad.left - 8, pad.top + t * (height - pad.top - pad.bottom) / 4 + 4);
    }
    ctx.textAlign = 'center';
    var labelStep = Math.max(1, Math.ceil(pathway.length / 6));
    pathway.forEach(function (row, i) {
      if (i % labelStep === 0 || i === pathway.length - 1) ctx.fillText(String(row.year), x(i), height - 17);
    });

    ctx.strokeStyle = '#701f2b'; ctx.lineWidth = 2.5; ctx.beginPath();
    pathway.forEach(function (row, i) { if (i === 0) ctx.moveTo(x(i), y(row.cumulative_net_emissions)); else ctx.lineTo(x(i), y(row.cumulative_net_emissions)); });
    ctx.stroke();
    ctx.strokeStyle = '#111111'; ctx.lineWidth = 1.5; ctx.setLineDash([7, 5]); ctx.beginPath();
    pathway.forEach(function (row, i) { if (i === 0) ctx.moveTo(x(i), y(row.carbon_budget)); else ctx.lineTo(x(i), y(row.carbon_budget)); });
    ctx.stroke(); ctx.setLineDash([]);
    ctx.textAlign = 'left'; ctx.fillStyle = '#701f2b'; ctx.fillText('Cumulative net emissions', pad.left, 13);
    ctx.fillStyle = '#111111'; ctx.fillText('Declared budget', pad.left + 170, 13);
  }

  function render(root, analysis) {
    root.querySelector('[data-scar-cumulative]').textContent = format(analysis.diagnostics.cumulative_net_emissions, 1);
    root.querySelector('[data-scar-remaining]').textContent = format(analysis.diagnostics.remaining_budget, 1);
    root.querySelector('[data-scar-overshoot]').textContent = analysis.diagnostics.overshoot_year == null ? 'None' : String(analysis.diagnostics.overshoot_year);
    root.querySelector('[data-scar-natural]').textContent = format(analysis.diagnostics.natural_capital_closing_stock, 1);

    var budgetStatus = root.querySelector('[data-scar-budget-status]');
    var budgetBoundary = analysis.boundary_assessment[0];
    budgetStatus.textContent = budgetBoundary.status.replace('_', ' ');
    budgetStatus.dataset.state = budgetBoundary.status;
    var reconciliation = root.querySelector('[data-scar-reconciliation]');
    reconciliation.textContent = 'Reconciled';
    reconciliation.dataset.state = 'within';

    drawChart(root.querySelector('[data-scar-chart]'), analysis.carbon_pathway);

    var contribution = analysis.kaya_decomposition.contributions[0];
    var kayaFields = [
      ['Population', contribution.population_effect],
      ['Affluence', contribution.affluence_effect],
      ['Energy intensity', contribution.energy_intensity_effect],
      ['Carbon intensity', contribution.carbon_intensity_effect]
    ];
    root.querySelector('[data-scar-kaya]').innerHTML = kayaFields.map(function (entry) {
      return '<article><span>' + entry[0] + '</span><strong>' + (entry[1] >= 0 ? '+' : '') + format(entry[1], 2) + '</strong></article>';
    }).join('');

    root.querySelector('[data-scar-natural-table]').innerHTML = analysis.natural_capital_account.map(function (row) {
      var additions = row.regeneration + row.restoration + row.additions;
      var losses = row.extraction + row.degradation + row.damages;
      return '<tr><td>' + row.time + '</td><td>' + format(row.opening_stock, 1) + '</td><td>' + format(additions, 1) + '</td><td>' + format(losses, 1) + '</td><td>' + format(row.closing_stock, 1) + '</td><td>' + (row.net_change >= 0 ? '+' : '') + format(row.net_change, 1) + '</td></tr>';
    }).join('');

    root.querySelector('[data-scar-boundaries]').innerHTML = analysis.boundary_assessment.map(function (row) {
      var detail = row.direction === 'at_or_below' ? 'Limit ' + format(row.upper, 1) : 'Floor ' + format(row.lower, 1);
      return '<article class="scar-demo__boundary" data-state="' + row.status + '"><strong>' + row.boundary_title + '</strong><span>' + row.status.toUpperCase() + ' · Value ' + format(row.value, 1) + ' · ' + detail + '</span></article>';
    }).join('');
  }

  function downloadJSON(data) {
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'catalyst-analytics-r-climate-accounting.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function init(root) {
    var form = root.querySelector('[data-scar-form]');
    var latest = null;
    function run(event) {
      if (event) event.preventDefault();
      try {
        latest = buildAnalysis(form);
        render(root, latest);
      } catch (error) {
        window.alert(error.message);
      }
    }
    form.addEventListener('submit', run);
    root.querySelector('[data-scar-download]').addEventListener('click', function () {
      if (!latest) run();
      if (latest) downloadJSON(latest);
    });
    root.querySelector('[data-scar-reset]').addEventListener('click', function () {
      form.reset();
      run();
    });
    window.addEventListener('resize', function () { if (latest) drawChart(root.querySelector('[data-scar-chart]'), latest.carbon_pathway); });
    run();
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-scar-demo]').forEach(init);
  });
}());
