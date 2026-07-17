<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for climate, carbon, and natural-capital accounting in Catalyst Analytics R.
 * Version: 1.5.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SCAR_DEMO_VERSION', '1.5.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '0.6.0');

function scar_demo_assets() {
    $base = plugin_dir_url(__FILE__);
    wp_enqueue_style(
        'catalyst-analytics-r-demo',
        $base . 'assets/catalyst-analytics-r-demo.css',
        array(),
        SCAR_DEMO_VERSION
    );
    wp_enqueue_script(
        'catalyst-analytics-r-demo',
        $base . 'assets/catalyst-analytics-r-demo.js',
        array(),
        SCAR_DEMO_VERSION,
        true
    );
}
add_action('wp_enqueue_scripts', 'scar_demo_assets');

function scar_demo_shortcode() {
    ob_start();
    ?>
    <section class="scar-demo" data-scar-demo>
      <header class="scar-demo__header">
        <p class="scar-demo__eyebrow">Catalyst Analytics R v0.6.0</p>
        <h3>Climate, carbon, and natural-capital accounting</h3>
        <p>
          Build a transparent emissions pathway, track a declared carbon budget,
          decompose emissions drivers, reconcile natural-capital stocks and flows,
          and inspect boundary signals in one governed browser record.
        </p>
      </header>

      <div class="scar-demo__grid">
        <form class="scar-demo__form" data-scar-form>
          <fieldset>
            <legend>Carbon pathway</legend>
            <div class="scar-demo__row">
              <label>Start year
                <input type="number" name="startYear" value="2025" min="1900" max="2200">
              </label>
              <label>End year
                <input type="number" name="endYear" value="2035" min="1901" max="2250">
              </label>
            </div>
            <div class="scar-demo__row">
              <label>Carbon budget
                <input type="number" name="carbonBudget" value="650" min="0" step="1">
              </label>
              <label>Starting emissions
                <input type="number" name="startingEmissions" value="100" min="0" step="0.1">
              </label>
            </div>
            <div class="scar-demo__row">
              <label>Annual decarbonization (%)
                <input type="number" name="decarbonization" value="9" min="0" max="100" step="0.1">
              </label>
              <label>Starting removals
                <input type="number" name="startingRemovals" value="5" min="0" step="0.1">
              </label>
            </div>
            <div class="scar-demo__row">
              <label>Annual removals growth (%)
                <input type="number" name="removalsGrowth" value="18" min="-100" max="300" step="0.1">
              </label>
              <label>Target net emissions
                <input type="number" name="targetNet" value="0" step="0.1">
              </label>
            </div>
          </fieldset>

          <fieldset>
            <legend>Kaya drivers</legend>
            <div class="scar-demo__row">
              <label>GDP growth (%)
                <input type="number" name="gdpGrowth" value="2.5" min="-20" max="30" step="0.1">
              </label>
              <label>Population growth (%)
                <input type="number" name="populationGrowth" value="0.8" min="-10" max="10" step="0.1">
              </label>
            </div>
            <label>Energy-intensity improvement (%)
              <input type="number" name="energyIntensityImprovement" value="3.5" min="-20" max="50" step="0.1">
            </label>
          </fieldset>

          <fieldset>
            <legend>Natural-capital account</legend>
            <div class="scar-demo__row">
              <label>Opening stock
                <input type="number" name="naturalOpening" value="1000" min="0" step="1">
              </label>
              <label>Boundary floor
                <input type="number" name="naturalFloor" value="950" min="0" step="1">
              </label>
            </div>
            <div class="scar-demo__row">
              <label>Annual regeneration
                <input type="number" name="regeneration" value="18" min="0" step="0.1">
              </label>
              <label>Annual restoration
                <input type="number" name="restoration" value="7" min="0" step="0.1">
              </label>
            </div>
            <div class="scar-demo__row scar-demo__row--three">
              <label>Extraction
                <input type="number" name="extraction" value="14" min="0" step="0.1">
              </label>
              <label>Degradation
                <input type="number" name="degradation" value="6" min="0" step="0.1">
              </label>
              <label>Damages
                <input type="number" name="damages" value="3" min="0" step="0.1">
              </label>
            </div>
          </fieldset>

          <button class="scar-demo__run" type="submit">Run governed accounting</button>
          <p class="scar-demo__form-note">
            Units are synthetic indices for demonstration. A production analysis must document source boundaries,
            gases, GWP basis, allocation method, valuation method, and review status.
          </p>
        </form>

        <div class="scar-demo__results" aria-live="polite">
          <div class="scar-demo__scorecards">
            <article><span>Cumulative net</span><strong data-scar-cumulative>--</strong><small>emissions units</small></article>
            <article><span>Budget remaining</span><strong data-scar-remaining>--</strong><small>emissions units</small></article>
            <article><span>Overshoot</span><strong data-scar-overshoot>--</strong><small>first year</small></article>
            <article><span>Natural capital</span><strong data-scar-natural>--</strong><small>closing stock</small></article>
          </div>

          <section class="scar-demo__panel">
            <div class="scar-demo__panel-head">
              <div><p class="scar-demo__kicker">Carbon account</p><h4>Cumulative emissions and declared budget</h4></div>
              <span data-scar-budget-status class="scar-demo__status">Not run</span>
            </div>
            <div class="scar-demo__chart-wrap">
              <canvas data-scar-chart width="760" height="300" aria-label="Carbon budget pathway chart"></canvas>
            </div>
          </section>

          <section class="scar-demo__panel">
            <div class="scar-demo__panel-head">
              <div><p class="scar-demo__kicker">Driver decomposition</p><h4>Kaya identity contributions</h4></div>
            </div>
            <div class="scar-demo__kaya" data-scar-kaya></div>
          </section>

          <section class="scar-demo__panel">
            <div class="scar-demo__panel-head">
              <div><p class="scar-demo__kicker">Stock and flow</p><h4>Natural-capital reconciliation</h4></div>
              <span data-scar-reconciliation class="scar-demo__status">Not run</span>
            </div>
            <div class="scar-demo__table-wrap">
              <table class="scar-demo__table">
                <thead><tr><th>Year</th><th>Opening</th><th>Additions</th><th>Losses</th><th>Closing</th><th>Change</th></tr></thead>
                <tbody data-scar-natural-table></tbody>
              </table>
            </div>
          </section>

          <section class="scar-demo__panel scar-demo__boundary-panel">
            <div class="scar-demo__panel-head">
              <div><p class="scar-demo__kicker">Review signals</p><h4>Boundary assessment</h4></div>
            </div>
            <div class="scar-demo__boundaries" data-scar-boundaries></div>
          </section>

          <div class="scar-demo__actions">
            <button type="button" data-scar-download>Download governed JSON</button>
            <button type="button" data-scar-reset>Restore example</button>
          </div>
        </div>
      </div>

      <details class="scar-demo__details">
        <summary>Contract and interpretation boundary</summary>
        <p>
          This browser companion maps to Catalyst Analytics R v0.6.0 contracts but does not execute R.
          It uses deterministic educational calculations. It does not verify inventories, allocate a scientifically
          defensible carbon budget, value natural capital, establish compliance, or make an autonomous decision.
        </p>
      </details>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
