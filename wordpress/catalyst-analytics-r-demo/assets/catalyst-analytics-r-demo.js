(function () {
  'use strict';
  var CONTRACT = {
    schema_version: '1.0.0',
    compatible_repository_version: '1.0.0',
    plugin_version: '2.0.0',
    project_contract_version: '1.0.0',
    publication_contract_version: '1.0.0',
    parity_status: 'mapped_project_contract_not_r_execution'
  };

  function value(form, name) { return form.elements[name].value.trim(); }
  function number(form, name) { var n = Number(form.elements[name].value); if (!Number.isFinite(n)) throw new Error('Invalid value for ' + name); return n; }
  function now() { return new Date().toISOString(); }
  function slug(text) { return text.toLowerCase().replace(/[^a-z0-9._-]+/g, '-').replace(/^-|-$/g, '') || 'project'; }
  function stable(value) {
    if (Array.isArray(value)) return '[' + value.map(stable).join(',') + ']';
    if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(function (key) { return JSON.stringify(key) + ':' + stable(value[key]); }).join(',') + '}';
    return JSON.stringify(value);
  }
  function hash(text) {
    var h1 = 0x811c9dc5, h2 = 0x811c9dc5, i;
    for (i = 0; i < text.length; i += 1) { h1 ^= text.charCodeAt(i); h1 = Math.imul(h1, 0x01000193); h2 ^= text.charCodeAt(text.length - 1 - i); h2 = Math.imul(h2, 0x01000193); }
    function hex(n) { return ('00000000' + (n >>> 0).toString(16)).slice(-8); }
    return hex(h1) + hex(h2) + hex(h1 ^ h2) + hex(Math.imul(h1, h2));
  }
  function scenario(id, title, role, savings, emissions) {
    return { schema_version: '1.0.0', id: id, title: title, role: role, model: { id: 'khncpa', version: '1.0.0' }, time: { start: 0, end: 20, step: 1, unit: 'year', values: Array.from({ length: 21 }, function (_, i) { return i; }) }, policy: { s: savings, e: role === 'baseline' ? 0.03 : 0.08, a: role === 'baseline' ? 0.01 : 0.10 }, parameters: { emissions_intensity: emissions, regen: role === 'baseline' ? 0.02 : 0.05 }, constraints: { emissions_budget: 8 }, assumptions: [{ id: id + '-assumption', statement: 'Browser approximation preserves project structure but not R numerical parity.', status: 'declared' }], review: { status: 'draft', reviewed_by: [], notes: [] } };
  }
  function runRecord(id, scenarioRecord) {
    var inputs = { scenario: scenarioRecord, method: 'browser-educational-approximation' };
    var terminal = { produced_capital: 1 + scenarioRecord.policy.s * 1.5, natural_capital: 1 + scenarioRecord.parameters.regen * 4 - scenarioRecord.parameters.emissions_intensity * 0.2, cumulative_emissions: scenarioRecord.parameters.emissions_intensity * 20 * (1 - scenarioRecord.policy.e) };
    var result = { terminal: terminal, indicators: { prosperity: terminal.produced_capital, natural_capital: terminal.natural_capital, cumulative_emissions: terminal.cumulative_emissions } };
    return { schema_version: '1.0.0', id: id, label: scenarioRecord.title + ' browser run', status: 'completed', scenario_ids: [scenarioRecord.id], model: scenarioRecord.model, created_at: now(), completed_at: now(), package: { name: 'catalystanalyticsr-browser-companion', version: CONTRACT.plugin_version }, environment: { schema_version: '1.0.0', runtime: 'browser', user_agent: navigator.userAgent }, input_hash: hash(stable(inputs)), output_hash: hash(stable(result)), inputs: inputs, result_summary: { type: 'browser_scenario_run', terminal: terminal }, result: result, warnings: ['Browser calculations are not R numerical parity.'], errors: [], review_status: 'unreviewed' };
  }
  function build(form) {
    var projectId = value(form, 'projectId') || slug(value(form, 'title'));
    var baseline = scenario('baseline', 'Reference baseline', 'baseline', number(form, 'baselineSavings'), number(form, 'baselineEmissions'));
    var policy = scenario('transition-policy', 'Transition policy', 'intervention', number(form, 'policySavings'), number(form, 'policyEmissions'));
    var baselineRun = runRecord('baseline-run', baseline), policyRun = runRecord('policy-run', policy);
    var review = value(form, 'review'), publication = value(form, 'publication'), created = now();
    var project = {
      schema_version: '1.0.0', project_type: 'reproducible_analytical_project', id: projectId, title: value(form, 'title'), description: value(form, 'question'), owner: value(form, 'owner'),
      scope: { geography: 'WORLD', sector: 'all', decision_context: 'educational browser project' }, tags: ['reproducibility', 'scenario-comparison'],
      scenarios: { baseline: baseline, 'transition-policy': policy }, datasets: {}, models: { 'khncpa@1.0.0': { id: 'khncpa', version: '1.0.0', title: 'KH-NC-PA vector dynamics model' } }, parameter_sets: {},
      runs: { 'baseline-run': baselineRun, 'policy-run': policyRun }, indicators: {}, plots: {},
      notes: [{ id: 'interpretation-1', text: value(form, 'note'), author: value(form, 'owner'), run_ids: ['baseline-run', 'policy-run'], status: review === 'approved' ? 'approved' : 'draft', created_at: created }],
      reviews: [{ id: 'review-1', reviewer: value(form, 'owner') || 'Reviewer', decision: review, comments: 'Browser project review record.', scope: 'project', run_ids: ['baseline-run', 'policy-run'], reviewed_at: created }],
      snapshots: [], publications: [], environment: { schema_version: '1.0.0', captured_at: created, r: { version: 'not executed', platform: 'browser', arch: navigator.platform }, operating_system: { sysname: navigator.platform }, packages: [{ name: 'catalyst-analytics-r-demo', version: CONTRACT.plugin_version, installed: true }] },
      metadata: { package_version: CONTRACT.compatible_repository_version, created_at: created, updated_at: created, review_status: review === 'approved' ? 'approved' : 'in_review', publication_status: publication }
    };
    var fingerprintRecord = JSON.parse(JSON.stringify(project)); delete fingerprintRecord.environment.captured_at; delete fingerprintRecord.metadata.created_at; delete fingerprintRecord.metadata.updated_at;
    var fingerprint = hash(stable(fingerprintRecord));
    project.snapshots.push({ id: 'snapshot-1', note: 'Browser publication candidate', created_at: created, project_fingerprint: fingerprint, counts: { scenarios: 2, datasets: 0, models: 1, parameter_sets: 0, runs: 2, indicators: 0, plots: 0, notes: 1, reviews: 1 } });
    var publicationRecord = { schema_version: '1.0.0', export_type: 'reproducible_analytical_project_publication', project_id: project.id, project_fingerprint: fingerprint, package: { name: 'catalystanalyticsr', version: CONTRACT.compatible_repository_version }, created_at: created, formats: ['json', 'csv', 'markdown', 'html', 'quarto'], files: ['project.json', 'run-index.csv', 'analytical-publication.md', 'analytical-publication.html', 'analytical-publication.qmd', 'decision-studio-handoff.json', 'knowledge-library-methodology.json'], review_status: project.metadata.review_status, publication_status: publication };
    var decision = { schema_version: '1.0.0', handoff_type: 'decision_studio_analytical_project', project_id: project.id, project_fingerprint: fingerprint, title: project.title, alternatives: [baseline, policy], analytical_evidence: [baselineRun.result_summary, policyRun.result_summary], interpretations: project.notes, reviews: project.reviews, decision_boundary: { human_decision_required: true, approval_not_inferred_from_reproducibility: true }, created_at: created };
    var knowledge = { schema_version: '1.0.0', handoff_type: 'knowledge_library_methodology_package', project_id: project.id, project_fingerprint: fingerprint, title: project.title + ' - Methodology Record', abstract: project.description, models: project.models, assumptions: baseline.assumptions.concat(policy.assumptions), runs: [baselineRun, policyRun].map(function (r) { return { id: r.id, input_hash: r.input_hash, output_hash: r.output_hash, result_summary: r.result_summary }; }), interpretations: project.notes, review_record: project.reviews, created_at: created };
    return { schema_version: '1.0.0', export_type: 'browser_reproducible_sustainability_analytics_engine', contract: CONTRACT, project: project, run_index: [baselineRun, policyRun].map(function (r) { return { id: r.id, label: r.label, status: r.status, input_hash: r.input_hash, output_hash: r.output_hash, review_status: r.review_status }; }), publication: publicationRecord, handoffs: { decision_studio: decision, knowledge_library: knowledge }, review_boundary: { r_not_executed: true, reproducible_not_necessarily_valid: true, human_review_required: true, not_forecast_or_professional_advice: true } };
  }
  function format(n) { return Number(n).toFixed(3).replace(/\.000$/, ''); }
  function render(root, payload) {
    var p = payload.project, runs = payload.run_index;
    root.querySelector('[data-scar-fingerprint]').textContent = payload.publication.project_fingerprint.slice(0, 12) + '...';
    root.querySelector('[data-scar-scenarios]').textContent = Object.keys(p.scenarios).length;
    root.querySelector('[data-scar-runs]').textContent = runs.length;
    root.querySelector('[data-scar-status]').textContent = p.metadata.review_status + ' / ' + p.metadata.publication_status;
    root.querySelector('[data-scar-review]').textContent = p.reviews[0].decision;
    root.querySelector('[data-scar-review]').dataset.state = p.reviews[0].decision;
    root.querySelector('[data-scar-note]').textContent = p.notes[0].text;
    root.querySelector('[data-scar-path]').innerHTML = ['Question', 'Scenarios', 'Runs', 'Hashes', 'Interpretation', 'Review', 'Publication', 'Handoffs'].map(function (label, i) { return '<span><b>' + (i + 1) + '</b>' + label + '</span>'; }).join('<i>→</i>');
    root.querySelector('[data-scar-run-index]').innerHTML = runs.map(function (run) { return '<div><span>' + run.label + '</span><strong>' + run.status + '</strong><small>in ' + run.input_hash.slice(0, 8) + ' · out ' + run.output_hash.slice(0, 8) + '</small></div>'; }).join('');
    root.querySelector('[data-scar-integrity]').innerHTML = [
      ['Project fingerprint', payload.publication.project_fingerprint.slice(0, 16)], ['Runtime', 'Browser companion'], ['Repository contract', CONTRACT.compatible_repository_version], ['Snapshots', String(p.snapshots.length)], ['Review records', String(p.reviews.length)]
    ].map(function (row) { return '<div><span>' + row[0] + '</span><strong>' + row[1] + '</strong></div>'; }).join('');
    root.querySelector('[data-scar-artifacts]').innerHTML = payload.publication.files.map(function (file) { return '<span>' + file + '</span>'; }).join('');
    root.querySelector('[data-scar-handoffs]').innerHTML = '<article><strong>Decision Studio</strong><p>' + payload.handoffs.decision_studio.alternatives.length + ' alternatives and human-decision boundary.</p></article><article><strong>Knowledge Library</strong><p>Methodology, assumptions, hashes, interpretation, and review record.</p></article>';
  }
  function markdown(payload) {
    var p = payload.project;
    return ['# ' + p.title, '', '**Project ID:** `' + p.id + '`  ', '**Owner:** ' + (p.owner || 'Not specified') + '  ', '**Fingerprint:** `' + payload.publication.project_fingerprint + '`  ', '**Review:** ' + p.metadata.review_status + '  ', '', '## Analytical question', p.description, '', '## Runs', ''].concat(payload.run_index.map(function (r) { return '- **' + r.label + '**: ' + r.status + '; input `' + r.input_hash + '`; output `' + r.output_hash + '`'; })).concat(['', '## Interpretation', p.notes[0].text, '', '## Review boundary', 'This browser publication preserves structure and hashes but does not execute R or establish external validity.']).join('\n');
  }
  function download(name, type, text) { var blob = new Blob([text], { type: type }), url = URL.createObjectURL(blob), link = document.createElement('a'); link.href = url; link.download = name; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url); }
  function init(root) {
    var form = root.querySelector('[data-scar-form]'), latest = null;
    function run(event) { if (event) event.preventDefault(); try { latest = build(form); render(root, latest); } catch (error) { window.alert(error.message); } }
    form.addEventListener('submit', run);
    root.querySelector('[data-scar-json]').addEventListener('click', function () { if (!latest) run(); if (latest) download(latest.project.id + '-project-publication.json', 'application/json', JSON.stringify(latest, null, 2)); });
    root.querySelector('[data-scar-markdown]').addEventListener('click', function () { if (!latest) run(); if (latest) download(latest.project.id + '-analytical-publication.md', 'text/markdown', markdown(latest)); });
    root.querySelector('[data-scar-reset]').addEventListener('click', function () { form.reset(); run(); });
    run();
  }
  document.addEventListener('DOMContentLoaded', function () { document.querySelectorAll('[data-scar-demo]').forEach(init); });
}());
