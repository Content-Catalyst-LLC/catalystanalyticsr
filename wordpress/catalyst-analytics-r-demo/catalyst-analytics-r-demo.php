<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for inclusive wealth, human development, and distribution analysis in Catalyst Analytics R.
 * Version: 1.6.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SCAR_DEMO_VERSION', '1.6.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '0.7.0');

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
        <p class="scar-demo__eyebrow">Catalyst Analytics R v0.7.0</p>
        <h3>Inclusive wealth, human development, and distribution</h3>
        <p>
          Reconcile produced, human, and natural capital; decompose Adjusted Net Savings;
          inspect human-development and distribution signals; and test whether a composite
          score is overly dependent on declared weights.
        </p>
      </header>

      <div class="scar-demo__grid">
        <form class="scar-demo__form" data-scar-form>
          <fieldset>
            <legend>Scope</legend>
            <label>Entity
              <input type="text" name="entity" value="Example region">
            </label>
            <div class="scar-demo__row">
              <label>Start year<input type="number" name="startYear" value="2025"></label>
              <label>End year<input type="number" name="endYear" value="2035"></label>
            </div>
            <div class="scar-demo__row">
              <label>Starting population<input type="number" name="populationStart" value="5" min="0.01" step="0.01"></label>
              <label>Ending population<input type="number" name="populationEnd" value="5.3" min="0.01" step="0.01"></label>
            </div>
          </fieldset>

          <fieldset>
            <legend>Capital stocks</legend>
            <div class="scar-demo__capital-head"><span>Capital</span><span>Opening</span><span>Closing</span><span>Shadow price</span></div>
            <div class="scar-demo__capital-row"><strong>Produced</strong><input aria-label="Produced opening" type="number" name="producedOpening" value="500" min="0"><input aria-label="Produced closing" type="number" name="producedClosing" value="607" min="0"><input aria-label="Produced shadow price" type="number" name="producedPrice" value="1" min="0.01" step="0.01"></div>
            <div class="scar-demo__capital-row"><strong>Human</strong><input aria-label="Human opening" type="number" name="humanOpening" value="400" min="0"><input aria-label="Human closing" type="number" name="humanClosing" value="478" min="0"><input aria-label="Human shadow price" type="number" name="humanPrice" value="1.2" min="0.01" step="0.01"></div>
            <div class="scar-demo__capital-row"><strong>Natural</strong><input aria-label="Natural opening" type="number" name="naturalOpening" value="300" min="0"><input aria-label="Natural closing" type="number" name="naturalClosing" value="298" min="0"><input aria-label="Natural shadow price" type="number" name="naturalPrice" value="1.5" min="0.01" step="0.01"></div>
          </fieldset>

          <fieldset>
            <legend>Adjusted Net Savings</legend>
            <div class="scar-demo__row"><label>Gross savings<input type="number" name="grossSavings" value="94" min="0"></label><label>GNI<input type="number" name="gni" value="1220" min="0.01"></label></div>
            <div class="scar-demo__row"><label>Depreciation<input type="number" name="depreciation" value="25" min="0"></label><label>Education investment<input type="number" name="education" value="27" min="0"></label></div>
            <div class="scar-demo__row"><label>Health investment<input type="number" name="health" value="16" min="0"></label><label>Resource depletion<input type="number" name="depletion" value="9" min="0"></label></div>
            <div class="scar-demo__row"><label>Pollution damages<input type="number" name="pollution" value="4" min="0"></label><label>Climate damages<input type="number" name="climate" value="6" min="0"></label></div>
          </fieldset>

          <fieldset>
            <legend>Human development</legend>
            <div class="scar-demo__row"><label>Life expectancy<input type="number" name="life" value="74" min="0" max="100" step="0.1"></label><label>Income per capita<input type="number" name="income" value="19300" min="1"></label></div>
            <div class="scar-demo__row"><label>Expected schooling<input type="number" name="expectedSchool" value="14" min="0" max="25" step="0.1"></label><label>Mean schooling<input type="number" name="meanSchool" value="9.8" min="0" max="25" step="0.1"></label></div>
          </fieldset>

          <fieldset>
            <legend>Distribution and score</legend>
            <label>Quintile resource values
              <input type="text" name="quintiles" value="18, 31, 45, 63, 98">
            </label>
            <label>Social floor<input type="number" name="socialFloor" value="25" min="0"></label>
            <p class="scar-demo__micro">Composite weights</p>
            <div class="scar-demo__row scar-demo__row--four">
              <label>Wealth<input type="number" name="wealthWeight" value="30" min="0" max="100"></label>
              <label>Savings<input type="number" name="savingsWeight" value="25" min="0" max="100"></label>
              <label>Human<input type="number" name="humanWeight" value="25" min="0" max="100"></label>
              <label>Natural<input type="number" name="naturalWeight" value="20" min="0" max="100"></label>
            </div>
          </fieldset>

          <button class="scar-demo__run" type="submit">Run inclusive analysis</button>
          <p class="scar-demo__form-note">Values are synthetic. Production use requires documented sources, valuation methods, distribution weights, social floors, and review status.</p>
        </form>

        <div class="scar-demo__results" aria-live="polite">
          <div class="scar-demo__scorecards">
            <article><span>Inclusive wealth</span><strong data-scar-wealth>--</strong><small>closing valued stock</small></article>
            <article><span>Per capita</span><strong data-scar-per-capita>--</strong><small>closing wealth</small></article>
            <article><span>Adjusted savings</span><strong data-scar-ans>--</strong><small>percent of GNI</small></article>
            <article><span>Composite score</span><strong data-scar-score>--</strong><small>0-100</small></article>
          </div>

          <section class="scar-demo__panel">
            <div class="scar-demo__panel-head"><div><p class="scar-demo__kicker">Capital account</p><h4>Opening and closing capital values</h4></div><span class="scar-demo__status" data-scar-generation>Not run</span></div>
            <div class="scar-demo__chart-wrap"><canvas data-scar-chart width="760" height="280" aria-label="Capital account chart"></canvas></div>
            <div class="scar-demo__composition" data-scar-composition></div>
          </section>

          <div class="scar-demo__panel-grid">
            <section class="scar-demo__panel">
              <p class="scar-demo__kicker">Savings decomposition</p><h4>Adjusted Net Savings</h4>
              <div class="scar-demo__ledger" data-scar-ans-ledger></div>
            </section>
            <section class="scar-demo__panel">
              <p class="scar-demo__kicker">Human development</p><h4>Dimension indices</h4>
              <div class="scar-demo__dimensions" data-scar-hdi></div>
            </section>
          </div>

          <section class="scar-demo__panel">
            <div class="scar-demo__panel-head"><div><p class="scar-demo__kicker">Distribution</p><h4>Quintile resources and social floor</h4></div><span class="scar-demo__status" data-scar-floor>Not run</span></div>
            <div class="scar-demo__distribution" data-scar-distribution></div>
            <div class="scar-demo__metrics" data-scar-distribution-metrics></div>
          </section>

          <section class="scar-demo__panel">
            <div class="scar-demo__panel-head"><div><p class="scar-demo__kicker">Composite governance</p><h4>Components and weight sensitivity</h4></div><span class="scar-demo__status" data-scar-sensitivity>Not run</span></div>
            <div class="scar-demo__components" data-scar-components></div>
          </section>

          <div class="scar-demo__actions">
            <button type="button" data-scar-download>Download governed JSON</button>
            <button type="button" data-scar-reset>Restore example</button>
          </div>
        </div>
      </div>

      <details class="scar-demo__details">
        <summary>Contract and interpretation boundary</summary>
        <p>This browser companion maps to Catalyst Analytics R v0.7.0 contracts but does not execute R. Shadow prices, capital measurement, human-development goalposts, social floors, distribution weights, discounting, and composite weights require human review. The output is not a forecast, compliance determination, autonomous decision, or professional advice.</p>
      </details>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
