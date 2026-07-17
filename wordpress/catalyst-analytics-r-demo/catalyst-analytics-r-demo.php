<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for reproducible analytical projects, run history, review, and publication handoffs in Catalyst Analytics R.
 * Version: 1.8.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SCAR_DEMO_VERSION', '1.8.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '0.9.0');

function scar_demo_assets() {
    $base = plugin_dir_url(__FILE__);
    wp_enqueue_style('catalyst-analytics-r-demo', $base . 'assets/catalyst-analytics-r-demo.css', array(), SCAR_DEMO_VERSION);
    wp_enqueue_script('catalyst-analytics-r-demo', $base . 'assets/catalyst-analytics-r-demo.js', array(), SCAR_DEMO_VERSION, true);
}
add_action('wp_enqueue_scripts', 'scar_demo_assets');

function scar_demo_shortcode() {
    ob_start();
    ?>
    <section class="scar-demo" data-scar-demo>
      <header class="scar-demo__header">
        <p class="scar-demo__eyebrow">Catalyst Analytics R v0.9.0</p>
        <h3>Reproducible project and publication studio</h3>
        <p>Assemble a project question, scenarios, run records, interpretation, review, snapshots, and platform handoffs into one portable analytical publication record.</p>
      </header>

      <div class="scar-demo__notice"><strong>Educational browser companion.</strong> This interface maps to the v0.9.0 project and publication contracts. It does not execute the R package, render Quarto, or establish external validity.</div>

      <form class="scar-demo__form" data-scar-form>
        <div class="scar-demo__controls">
          <label><span>Project title</span><input type="text" name="title" value="Transition Evidence Project" required></label>
          <label><span>Project owner</span><input type="text" name="owner" value="Sustainable Catalyst"></label>
          <label><span>Project id</span><input type="text" name="projectId" value="transition-evidence-project" pattern="[A-Za-z0-9._-]+" required></label>
          <label class="scar-demo__control--wide"><span>Analytical question</span><textarea name="question" rows="3">How does a transition policy compare with the declared baseline while preserving a reviewable analytical record?</textarea></label>
          <label><span>Baseline savings rate</span><input type="number" name="baselineSavings" min="0.05" max="0.60" step="0.01" value="0.18"></label>
          <label><span>Policy savings rate</span><input type="number" name="policySavings" min="0.05" max="0.60" step="0.01" value="0.25"></label>
          <label><span>Baseline emissions intensity</span><input type="number" name="baselineEmissions" min="0.01" max="1" step="0.01" value="0.30"></label>
          <label><span>Policy emissions intensity</span><input type="number" name="policyEmissions" min="0.01" max="1" step="0.01" value="0.14"></label>
          <label><span>Review decision</span><select name="review"><option value="pending">Pending</option><option value="changes_requested">Changes requested</option><option value="approved" selected>Approved</option><option value="rejected">Rejected</option></select></label>
          <label><span>Publication status</span><select name="publication"><option value="draft" selected>Draft</option><option value="reviewed">Reviewed</option><option value="published">Published</option></select></label>
          <label class="scar-demo__control--wide"><span>Interpretation note</span><textarea name="note" rows="3">The transition pathway improves the selected educational indicators, but results remain conditional on the declared model, parameters, and browser approximation.</textarea></label>
        </div>
        <div class="scar-demo__actions">
          <button type="submit">Build project record</button>
          <button type="button" class="scar-demo__secondary" data-scar-json>Export project JSON</button>
          <button type="button" class="scar-demo__secondary" data-scar-markdown>Export Markdown</button>
          <button type="button" class="scar-demo__link" data-scar-reset>Reset</button>
        </div>
      </form>

      <div class="scar-demo__metrics">
        <article><span>Project fingerprint</span><strong data-scar-fingerprint>--</strong></article>
        <article><span>Scenarios</span><strong data-scar-scenarios>--</strong></article>
        <article><span>Run records</span><strong data-scar-runs>--</strong></article>
        <article><span>Review / publication</span><strong data-scar-status>--</strong></article>
      </div>

      <div class="scar-demo__grid">
        <article class="scar-demo__panel scar-demo__panel--wide">
          <div class="scar-demo__panel-header"><div><p>Project graph</p><h4>Evidence preserved from question to publication</h4></div><span class="scar-demo__badge" data-scar-contract>Contract 1.0.0</span></div>
          <div class="scar-demo__path" data-scar-path></div>
        </article>

        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Scenario and run index</p><h4>Reproducible records</h4></div></div>
          <div class="scar-demo__ledger" data-scar-run-index></div>
        </article>

        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Integrity</p><h4>Hashes and environment</h4></div></div>
          <div class="scar-demo__checks" data-scar-integrity></div>
        </article>

        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Publication set</p><h4>Portable formats</h4></div></div>
          <div class="scar-demo__artifacts" data-scar-artifacts></div>
        </article>

        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Platform handoffs</p><h4>Decision and knowledge records</h4></div></div>
          <div class="scar-demo__handoffs" data-scar-handoffs></div>
        </article>

        <article class="scar-demo__panel scar-demo__panel--wide">
          <div class="scar-demo__panel-header"><div><p>Interpretation and review</p><h4>Human accountability record</h4></div><span class="scar-demo__badge" data-scar-review>Pending</span></div>
          <div class="scar-demo__review-grid"><section><h5>Interpretation</h5><p data-scar-note></p></section><section><h5>Review boundary</h5><p>Reproducibility preserves the analytical record; it does not establish causal validity, compliance, fitness for use, or professional approval.</p></section></div>
        </article>
      </div>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
