<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for calibration, validation, numerical testing, and model governance in Catalyst Analytics R.
 * Version: 1.7.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SCAR_DEMO_VERSION', '1.7.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '0.8.0');

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
        <p class="scar-demo__eyebrow">Catalyst Analytics R v0.8.0</p>
        <h3>Calibration, validation, and model governance</h3>
        <p>Fit one declared parameter to historical observations, reserve a holdout period, inspect residual and solver evidence, and document the exact use boundary required before a model can move through review.</p>
      </header>

      <div class="scar-demo__notice"><strong>Educational browser companion.</strong> This interface maps to the v0.8.0 governance contract but does not execute R or establish real-world model validity.</div>

      <form class="scar-demo__form" data-scar-form>
        <div class="scar-demo__controls">
          <label><span>Initial regeneration rate</span><input type="number" name="initial" min="0" max="0.08" step="0.001" value="0.020"></label>
          <label><span>Lower bound</span><input type="number" name="lower" min="0" max="0.08" step="0.001" value="0.000"></label>
          <label><span>Upper bound</span><input type="number" name="upper" min="0" max="0.20" step="0.001" value="0.080"></label>
          <label><span>Holdout years</span><input type="number" name="holdout" min="1" max="4" step="1" value="3"></label>
          <label><span>RMSE acceptance threshold</span><input type="number" name="threshold" min="0.001" max="0.10" step="0.001" value="0.010"></label>
          <label><span>Solver step</span><select name="solverStep"><option value="1">1 year</option><option value="0.5" selected>0.5 year</option><option value="0.25">0.25 year</option></select></label>
        </div>
        <div class="scar-demo__actions"><button type="submit">Run calibration and validation</button><button type="button" class="scar-demo__secondary" data-scar-download>Export governance JSON</button><button type="button" class="scar-demo__link" data-scar-reset>Reset</button></div>
      </form>

      <div class="scar-demo__metrics">
        <article><span>Calibrated rate</span><strong data-scar-estimate>--</strong></article>
        <article><span>Calibration RMSE</span><strong data-scar-calibration>--</strong></article>
        <article><span>Holdout RMSE</span><strong data-scar-holdout>--</strong></article>
        <article><span>Lifecycle recommendation</span><strong data-scar-status>--</strong></article>
      </div>

      <div class="scar-demo__grid">
        <article class="scar-demo__panel scar-demo__panel--wide">
          <div class="scar-demo__panel-header"><div><p>Historical and holdout evidence</p><h4>Observed versus calibrated pathway</h4></div><span class="scar-demo__badge" data-scar-validation>Not run</span></div>
          <canvas data-scar-chart aria-label="Observed and calibrated natural-capital pathway"></canvas>
          <div class="scar-demo__legend"><span><i data-kind="observed"></i>Observed</span><span><i data-kind="calibration"></i>Calibration fit</span><span><i data-kind="holdout"></i>Holdout prediction</span></div>
        </article>

        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Residual diagnostics</p><h4>Error evidence</h4></div></div>
          <div class="scar-demo__ledger" data-scar-residuals></div>
        </article>

        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Numerical validation</p><h4>Solver and stability checks</h4></div></div>
          <div class="scar-demo__checks" data-scar-numerical></div>
        </article>

        <article class="scar-demo__panel scar-demo__panel--wide">
          <div class="scar-demo__panel-header"><div><p>Model card</p><h4>Approved use boundary</h4></div><span class="scar-demo__badge" data-scar-governance>Experimental</span></div>
          <div class="scar-demo__governance">
            <section><h5>Intended use</h5><p>Educational synthetic-benchmark analysis and method development.</p></section>
            <section><h5>Prohibited use</h5><p>Forecasting, compliance determinations, investment decisions, or professional advice.</p></section>
            <section><h5>Approval scope</h5><p data-scar-scope>Pending validation.</p></section>
          </div>
          <div class="scar-demo__limitations" data-scar-limitations></div>
        </article>
      </div>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
