(function () {
  'use strict';

  var units = {
    year: 'year',
    gdp: 'currency_index',
    population: 'person_index',
    emissions: 'tCO2e_index',
    natural_capital: 'index',
    gross_savings: 'currency_index',
    depreciation: 'currency_index',
    depletion: 'currency_index',
    damages: 'currency_index',
    education_investment: 'currency_index'
  };

  function definition(id, title, description, formula, fields, unit, direction, aggregation, methodology) {
    return {
      id: id,
      version: '1.0.0',
      title: title,
      description: description,
      formula: formula,
      required_fields: fields,
      unit: unit,
      direction: direction,
      aggregation: aggregation,
      source: { type: 'derived', methodology: methodology },
      targets: [],
      metadata: { status: 'active', builtin: true, browser_contract: '1.0.0' }
    };
  }

  var registry = [
    definition('carbon_intensity', 'Carbon intensity', 'Emissions per unit of economic output.', 'emissions / gdp', ['emissions', 'gdp'], 'tCO2e/currency', 'lower_better', 'rowwise', 'Emissions divided by GDP.'),
    definition('gdp_per_capita', 'GDP per capita', 'Economic output divided by population.', 'gdp / population', ['gdp', 'population'], 'currency/person', 'higher_better', 'rowwise', 'GDP divided by population.'),
    definition('emissions_per_capita', 'Emissions per capita', 'Emissions divided by population.', 'emissions / population', ['emissions', 'population'], 'tCO2e/person', 'lower_better', 'rowwise', 'Emissions divided by population.'),
    definition('adjusted_net_savings', 'Adjusted net savings', 'Savings adjusted for depreciation, depletion, damages, and education investment.', 'gross_savings - depreciation - depletion - damages + education_investment', ['gross_savings', 'depreciation', 'depletion', 'damages', 'education_investment'], 'currency', 'higher_better', 'rowwise', 'Transparent simplified adjusted-net-savings identity.'),
    definition('cumulative_emissions', 'Cumulative emissions', 'Sum of emissions for each region.', 'sum(emissions)', ['emissions'], 'tCO2e', 'lower_better', 'sum', 'Unweighted sum across the supplied observations.'),
    definition('natural_capital_change', 'Natural-capital change', 'Final natural-capital value minus the first value for each region.', 'last(natural_capital) - first(natural_capital)', ['natural_capital'], 'index', 'higher_better', 'last_minus_first', 'Final value minus initial value in record order.')
  ];

  function escapeHTML(value) {
    return String(value).replace(/[&<>'"]/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char];
    });
  }

  function parseCSVLine(line) {
    var values = [], current = '', quoted = false;
    for (var i = 0; i < line.length; i += 1) {
      var char = line[i];
      if (char === '"') {
        if (quoted && line[i + 1] === '"') { current += '"'; i += 1; }
        else quoted = !quoted;
      } else if (char === ',' && !quoted) {
        values.push(current.trim()); current = '';
      } else current += char;
    }
    values.push(current.trim());
    return values;
  }

  function coerce(value) {
    if (value === '' || value.toLowerCase() === 'na' || value.toLowerCase() === 'null') return null;
    var numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : value;
  }

  function parseCSV(text) {
    var lines = text.replace(/\r/g, '').split('\n').filter(function (line) { return line.trim() !== ''; });
    if (lines.length < 2) throw new Error('CSV input must contain a header and at least one record.');
    var headers = parseCSVLine(lines[0]);
    if (headers.some(function (header) { return !header; })) throw new Error('Every CSV column must have a name.');
    if (new Set(headers).size !== headers.length) throw new Error('CSV column names must be unique.');
    var rows = lines.slice(1).map(function (line, index) {
      var values = parseCSVLine(line);
      if (values.length !== headers.length) throw new Error('Row ' + (index + 2) + ' has ' + values.length + ' fields; expected ' + headers.length + '.');
      return headers.reduce(function (record, header, fieldIndex) { record[header] = coerce(values[fieldIndex]); return record; }, {});
    });
    return { headers: headers, rows: rows };
  }

  function selectedDefinition(form) {
    var id = form.elements.indicator.value;
    return registry.filter(function (item) { return item.id === id; })[0];
  }

  function groupRows(rows) {
    return rows.reduce(function (groups, row) {
      var key = row.region === null || row.region === undefined ? 'dataset' : String(row.region);
      if (!groups[key]) groups[key] = [];
      groups[key].push(row);
      return groups;
    }, {});
  }

  function calculate(rows, indicator) {
    var missingFields = indicator.required_fields.filter(function (field) { return !Object.prototype.hasOwnProperty.call(rows[0], field); });
    if (missingFields.length) throw new Error('Selected indicator requires missing field(s): ' + missingFields.join(', ') + '.');
    var result = [];
    if (indicator.aggregation === 'rowwise') {
      rows.forEach(function (row) {
        var value;
        if (indicator.id === 'carbon_intensity') value = Number(row.emissions) / Math.max(Number(row.gdp), Number.EPSILON);
        if (indicator.id === 'gdp_per_capita') value = Number(row.gdp) / Math.max(Number(row.population), Number.EPSILON);
        if (indicator.id === 'emissions_per_capita') value = Number(row.emissions) / Math.max(Number(row.population), Number.EPSILON);
        if (indicator.id === 'adjusted_net_savings') value = Number(row.gross_savings) - Number(row.depreciation) - Number(row.depletion) - Number(row.damages) + Number(row.education_investment);
        result.push({ year: row.year, region: row.region, value: value });
      });
    } else {
      var groups = groupRows(rows);
      Object.keys(groups).sort().forEach(function (region) {
        var values = groups[region];
        var value;
        if (indicator.id === 'cumulative_emissions') value = values.reduce(function (sum, row) { return sum + Number(row.emissions); }, 0);
        if (indicator.id === 'natural_capital_change') {
          var ordered = values.slice().sort(function (a, b) { return Number(a.year) - Number(b.year); });
          value = Number(ordered[ordered.length - 1].natural_capital) - Number(ordered[0].natural_capital);
        }
        result.push({ region: region, value: value });
      });
    }
    if (result.some(function (row) { return !Number.isFinite(row.value); })) throw new Error('Indicator calculation produced a non-finite value. Check missing and zero-valued inputs.');
    return result;
  }

  function quality(parsed, indicator) {
    var rows = parsed.rows, headers = parsed.headers, flags = [], missing = 0;
    rows.forEach(function (row) { headers.forEach(function (field) { if (row[field] === null) missing += 1; }); });
    if (missing) flags.push({ code: 'missing_values', severity: 'warning', field: '', count: missing, message: missing + ' missing cell(s) were detected.' });
    var serialized = rows.map(function (row) { return JSON.stringify(row); });
    var duplicateRows = serialized.length - new Set(serialized).size;
    if (duplicateRows) flags.push({ code: 'duplicate_rows', severity: 'warning', field: '', count: duplicateRows, message: duplicateRows + ' duplicate row(s) were detected.' });
    var keys = rows.map(function (row) { return String(row.region) + '|' + String(row.year); });
    var duplicateKeys = keys.length - new Set(keys).size;
    if (duplicateKeys) flags.push({ code: 'duplicate_keys', severity: 'error', field: 'region,year', count: duplicateKeys, message: duplicateKeys + ' duplicate region/year key(s) were detected.' });
    indicator.required_fields.forEach(function (field) {
      var count = rows.filter(function (row) { return row[field] === null || row[field] === undefined; }).length;
      if (count) flags.push({ code: 'required_field_missing', severity: 'error', field: field, count: count, message: 'Required field `' + field + '` has ' + count + ' missing value(s).' });
    });
    if (!flags.length) flags.push({ code: 'quality_checks_passed', severity: 'ok', field: '', count: 0, message: 'No missing values, duplicate rows, duplicate keys, or absent required fields were detected.' });
    return { row_count: rows.length, column_count: headers.length, missing_cells: missing, duplicate_rows: duplicateRows, duplicate_keys: duplicateKeys, flags: flags };
  }

  function round(value, digits) {
    var factor = Math.pow(10, digits === undefined ? 4 : digits);
    return Math.round(value * factor) / factor;
  }

  function read(form) {
    var parsed = parseCSV(form.elements.csvData.value);
    var indicator = selectedDefinition(form);
    var report = quality(parsed, indicator);
    if (report.flags.some(function (flag) { return flag.severity === 'error'; })) throw new Error(report.flags.filter(function (flag) { return flag.severity === 'error'; }).map(function (flag) { return flag.message; }).join(' '));
    var values = calculate(parsed.rows, indicator);
    return {
      parsed: parsed,
      indicator: indicator,
      values: values,
      quality: report,
      dataset: {
        schema_version: '1.0.0',
        id: form.elements.datasetId.value.trim() || 'browser-dataset',
        title: form.elements.datasetTitle.value.trim() || 'Browser dataset',
        time_field: 'year',
        entity_fields: ['region'],
        units: units,
        source: {
          id: 'browser-declared-source',
          title: form.elements.datasetTitle.value.trim() || 'Browser dataset',
          publisher: form.elements.publisher.value.trim(),
          url: '',
          license: form.elements.license.value.trim(),
          retrieved_at: new Date().toISOString(),
          citation: '',
          metadata: { verification_status: 'unverified_user_declaration' }
        },
        currency: { code: form.elements.currency.value.trim(), price_year: Number(form.elements.priceYear.value) || null },
        records: parsed.rows
      }
    };
  }

  function trace(state) {
    return {
      schema_version: '1.0.0',
      indicator: state.indicator,
      dataset: { id: state.dataset.id, title: state.dataset.title, source: state.dataset.source, units: state.dataset.units },
      calculation: {
        calculated_at: new Date().toISOString(),
        compatible_repository_version: '0.5.0',
        browser_demo_version: '1.4.0',
        input_rows: state.parsed.rows.length,
        output_rows: state.values.length,
        required_fields: state.indicator.required_fields,
        formula: state.indicator.formula
      }
    };
  }

  function definitionHTML(indicator) {
    return '<h4>' + escapeHTML(indicator.title) + ' <small>v' + escapeHTML(indicator.version) + '</small></h4>' +
      '<p>' + escapeHTML(indicator.description) + ' Direction: <strong>' + escapeHTML(indicator.direction.replace('_', ' ')) + '</strong>. Required fields: ' + escapeHTML(indicator.required_fields.join(', ')) + '.</p>' +
      '<code class="scar-demo__formula">' + escapeHTML(indicator.formula) + '</code>';
  }

  function table(root, state) {
    var columns = state.values.length && Object.prototype.hasOwnProperty.call(state.values[0], 'year') ? ['region', 'year', 'value'] : ['region', 'value'];
    root.querySelector('[data-table-head]').innerHTML = '<tr>' + columns.map(function (field) { return '<th>' + escapeHTML(field) + '</th>'; }).join('') + '</tr>';
    root.querySelector('[data-table-body]').innerHTML = state.values.map(function (row) {
      return '<tr>' + columns.map(function (field) { return '<td>' + escapeHTML(field === 'value' ? round(row[field], 6) : row[field]) + '</td>'; }).join('') + '</tr>';
    }).join('');
  }

  function chart(svg, state) {
    var width = 760, height = 300, left = 62, right = 28, top = 28, bottom = 48;
    var values = state.values.map(function (row) { return row.value; });
    var minY = Math.min.apply(null, values), maxY = Math.max.apply(null, values);
    var pad = Math.max((maxY - minY) * 0.12, Math.abs(maxY || 1) * 0.05, 0.01); minY -= pad; maxY += pad;
    function y(value) { return top + (1 - (value - minY) / Math.max(maxY - minY, Number.EPSILON)) * (height - top - bottom); }
    var parts = ['<rect x="0" y="0" width="760" height="300" fill="#fbfaf6"/>'];
    for (var i = 0; i <= 4; i += 1) {
      var gy = top + i * (height - top - bottom) / 4;
      parts.push('<line x1="' + left + '" y1="' + gy + '" x2="' + (width - right) + '" y2="' + gy + '" stroke="#d9d2c4"/>');
      parts.push('<text x="8" y="' + (gy + 4) + '">' + round(maxY - i * (maxY - minY) / 4, 3) + '</text>');
    }
    if (state.indicator.aggregation === 'rowwise') {
      var groups = groupRows(state.values), colors = ['#7f1d1d', '#333333', '#6b5b3e', '#3d5a4f'];
      Object.keys(groups).sort().forEach(function (region, groupIndex) {
        var rows = groups[region].slice().sort(function (a, b) { return Number(a.year) - Number(b.year); });
        var years = rows.map(function (row) { return Number(row.year); }), minX = Math.min.apply(null, years), maxX = Math.max.apply(null, years);
        function x(year) { return left + (Number(year) - minX) / Math.max(maxX - minX, 1) * (width - left - right); }
        var path = rows.map(function (row, index) { return (index ? 'L ' : 'M ') + x(row.year) + ' ' + y(row.value); }).join(' ');
        parts.push('<path d="' + path + '" fill="none" stroke="' + colors[groupIndex % colors.length] + '" stroke-width="3"/>');
        rows.forEach(function (row) { parts.push('<circle cx="' + x(row.year) + '" cy="' + y(row.value) + '" r="4" fill="' + colors[groupIndex % colors.length] + '"/>'); });
        parts.push('<text x="' + (left + groupIndex * 135) + '" y="286" fill="' + colors[groupIndex % colors.length] + '">' + escapeHTML(region) + '</text>');
      });
    } else {
      var barWidth = Math.min(110, (width - left - right) / Math.max(state.values.length, 1) * 0.55);
      state.values.forEach(function (row, index) {
        var slot = (width - left - right) / state.values.length, x = left + index * slot + (slot - barWidth) / 2, yValue = y(row.value), zero = y(Math.max(0, minY));
        parts.push('<rect x="' + x + '" y="' + Math.min(yValue, zero) + '" width="' + barWidth + '" height="' + Math.max(2, Math.abs(zero - yValue)) + '" fill="#7f1d1d"/>');
        parts.push('<text x="' + (x + barWidth / 2 - 18) + '" y="286">' + escapeHTML(row.region) + '</text>');
      });
    }
    svg.innerHTML = parts.join('');
  }

  function renderState(root, state) {
    var average = state.values.reduce(function (sum, row) { return sum + row.value; }, 0) / state.values.length;
    root.querySelector('[data-result="rows"]').textContent = state.quality.row_count;
    root.querySelector('[data-result="dimensions"]').textContent = state.quality.column_count + ' fields';
    root.querySelector('[data-result="missing"]').textContent = state.quality.missing_cells;
    root.querySelector('[data-result="duplicates"]').textContent = state.quality.duplicate_keys;
    root.querySelector('[data-result="indicatorSummary"]').textContent = round(average, 4);
    root.querySelector('[data-result="indicatorUnit"]').textContent = 'average ' + state.indicator.unit;
    root.querySelector('[data-definition]').innerHTML = definitionHTML(state.indicator);
    root.querySelector('[data-quality-flags]').innerHTML = state.quality.flags.map(function (flag) { return '<li data-severity="' + escapeHTML(flag.severity) + '">' + escapeHTML(flag.message) + '</li>'; }).join('');
    table(root, state);
    chart(root.querySelector('[data-chart]'), state);
    var t = trace(state);
    root.querySelector('[data-trace]').innerHTML = [
      ['Dataset', state.dataset.id], ['Indicator', state.indicator.id + '@' + state.indicator.version],
      ['Formula', state.indicator.formula], ['Required fields', state.indicator.required_fields.join(', ')],
      ['Source status', 'unverified user declaration'], ['Input/output rows', t.calculation.input_rows + ' / ' + t.calculation.output_rows]
    ].map(function (entry) { return '<dt>' + escapeHTML(entry[0]) + '</dt><dd>' + escapeHTML(entry[1]) + '</dd>'; }).join('');
    root._scarState = state;
  }

  function renderError(root, error) {
    root.querySelector('[data-quality-flags]').innerHTML = '<li data-severity="error">' + escapeHTML(error.message) + '</li>';
    root.querySelector('[data-result="indicatorSummary"]').textContent = 'Invalid';
  }

  function render(root) {
    try { renderState(root, read(root.querySelector('[data-scar-form]'))); }
    catch (error) { renderError(root, error); }
  }

  function payload(root) {
    var state = root._scarState || read(root.querySelector('[data-scar-form]'));
    return {
      schema_version: '1.4.0',
      demo: 'Catalyst Analytics R Demo',
      demo_version: '1.4.0',
      engine: {
        type: 'browser_data_intake',
        compatible_repository_version: '0.5.0',
        parity_status: 'mapped_data_indicator_contract',
        dataset_contract_version: '1.0.0',
        indicator_contract_version: '1.0.0'
      },
      generated_at: new Date().toISOString(),
      dataset: state.dataset,
      quality: state.quality,
      indicator_registry: registry,
      indicator_result: { indicator: state.indicator, values: state.values },
      trace: trace(state),
      boundary: { source_verified: false, unit_compatibility_verified: false, causal_claim: false, professional_advice: false }
    };
  }

  function download(root) {
    var content = JSON.stringify(payload(root), null, 2), blob = new Blob([content], { type: 'application/json' });
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = 'catalyst-analytics-r-data-analysis.json';
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(function () { URL.revokeObjectURL(link.href); }, 500);
  }

  function copySummary(root) {
    var data = payload(root), result = data.indicator_result;
    var text = [
      'Catalyst Analytics R data analysis',
      'Dataset: ' + data.dataset.title,
      'Records: ' + data.quality.row_count,
      'Indicator: ' + result.indicator.title + ' v' + result.indicator.version,
      'Formula: ' + result.indicator.formula,
      'Quality flags: ' + data.quality.flags.length,
      'Boundary: source and unit compatibility remain unverified.'
    ].join('\n');
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text);
    else window.prompt('Copy analysis:', text);
  }

  function init(root) {
    var form = root.querySelector('[data-scar-form]');
    form.addEventListener('input', function () { render(root); });
    root.querySelector('[data-action="copy"]').addEventListener('click', function () { copySummary(root); });
    root.querySelector('[data-action="download"]').addEventListener('click', function () { download(root); });
    root.querySelector('[data-action="reset"]').addEventListener('click', function () { form.reset(); render(root); });
    render(root);
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-scar-demo]').forEach(init);
  });
})();
