<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Comparative browser demo for baseline-versus-policy scenario analysis, trade-off review, and canonical Catalyst Analytics R exports. Use shortcode [catalyst_analytics_r_demo].
 * Version: 1.2.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

function scar_demo_enqueue_assets() {
    $url = plugin_dir_url(__FILE__);
    $ver = '1.2.0';
    wp_enqueue_style('scar-demo-style', $url . 'assets/catalyst-analytics-r-demo.css', array(), $ver);
    wp_enqueue_script('scar-demo-script', $url . 'assets/catalyst-analytics-r-demo.js', array(), $ver, true);
}

function scar_demo_shortcode($atts = array(), $content = null) {
    scar_demo_enqueue_assets();
    ob_start();
    ?>
    <div class="scar-demo" data-scar-demo>
      <div class="scar-demo__header">
        <p class="scar-demo__eyebrow">Catalyst Analytics R Comparative Demo</p>
        <h3>Compare a baseline with a policy pathway</h3>
        <p>
          Run two simplified browser scenarios side by side. Review overlaid trajectories, terminal values,
          direction-aware deltas, emissions-budget status, trade-offs, and a canonical comparison export mapped
          to Catalyst Analytics R v0.3.0.
        </p>
      </div>

      <div class="scar-demo__grid">
        <form class="scar-demo__form" data-scar-form>
          <fieldset>
            <legend>Shared scope</legend>
            <label>
              Time horizon <span data-out="yearsOut">20 years</span>
              <input type="range" name="years" min="5" max="40" step="1" value="20">
            </label>
            <label>Initial produced capital <input type="number" name="initialCapital" min="10" max="1000" step="10" value="100"></label>
            <label>Initial human capital <input type="number" name="initialHuman" min="10" max="1000" step="10" value="100"></label>
            <label>Initial natural capital <input type="number" name="initialNatural" min="10" max="1000" step="10" value="100"></label>
            <label>Emissions budget <input type="number" name="emissionsBudget" min="10" max="1000" step="10" value="120"></label>
          </fieldset>

          <fieldset class="scar-demo__scenario scar-demo__scenario--baseline">
            <legend>Baseline</legend>
            <label>Scenario name <input type="text" name="baselineName" value="Reference baseline" maxlength="80"></label>
            <label>Savings / reinvestment <span data-out="baselineSavingsOut">18%</span><input type="range" name="baselineSavings" min="5" max="45" step="1" value="18"></label>
            <label>Emissions intensity <span data-out="baselineEmissionsOut">10%</span><input type="range" name="baselineEmissionsIntensity" min="1" max="20" step="1" value="10"></label>
            <label>Adaptation investment <span data-out="baselineAdaptOut">2%</span><input type="range" name="baselineAdaptation" min="0" max="25" step="1" value="2"></label>
            <label>Natural restoration <span data-out="baselineRestoreOut">1%</span><input type="range" name="baselineRestoration" min="0" max="20" step="1" value="1"></label>
            <label>Human / social investment <span data-out="baselineHumanOut">2%</span><input type="range" name="baselineHumanInvestment" min="0" max="20" step="1" value="2"></label>
          </fieldset>

          <fieldset class="scar-demo__scenario scar-demo__scenario--policy">
            <legend>Policy pathway</legend>
            <label>Scenario name <input type="text" name="policyName" value="Transition policy" maxlength="80"></label>
            <label>Savings / reinvestment <span data-out="policySavingsOut">24%</span><input type="range" name="policySavings" min="5" max="45" step="1" value="24"></label>
            <label>Emissions intensity <span data-out="policyEmissionsOut">5%</span><input type="range" name="policyEmissionsIntensity" min="1" max="20" step="1" value="5"></label>
            <label>Adaptation investment <span data-out="policyAdaptOut">10%</span><input type="range" name="policyAdaptation" min="0" max="25" step="1" value="10"></label>
            <label>Natural restoration <span data-out="policyRestoreOut">8%</span><input type="range" name="policyRestoration" min="0" max="20" step="1" value="8"></label>
            <label>Human / social investment <span data-out="policyHumanOut">7%</span><input type="range" name="policyHumanInvestment" min="0" max="20" step="1" value="7"></label>
          </fieldset>
        </form>

        <div class="scar-demo__results" aria-live="polite">
          <div class="scar-demo__scorecards">
            <article><span>Composite-score delta</span><strong data-result="scoreDelta">—</strong><em data-result="scoreNote">policy versus baseline</em></article>
            <article><span>Adjusted-savings delta</span><strong data-result="ansDelta">—</strong><em>final-period difference</em></article>
            <article><span>Emissions difference</span><strong data-result="emissionsDelta">—</strong><em data-result="budgetNote">cumulative total</em></article>
            <article><span>Trade-off status</span><strong data-result="tradeoff">—</strong><em data-result="paretoNote">direction-aware review</em></article>
          </div>

          <div class="scar-demo__chart-wrap">
            <div class="scar-demo__chart-head">
              <div>
                <h4>Overlaid trajectories</h4>
                <p>Baseline and policy pathways use the same horizon, starting conditions, and budget.</p>
              </div>
              <label class="scar-demo__metric-label">Metric
                <select data-chart-metric>
                  <option value="composite_score">Composite score</option>
                  <option value="produced_capital">Produced capital</option>
                  <option value="human_capital">Human capital</option>
                  <option value="natural_capital">Natural capital</option>
                  <option value="cumulative_emissions">Cumulative emissions</option>
                  <option value="adjusted_savings">Adjusted savings</option>
                </select>
              </label>
            </div>
            <svg class="scar-demo__chart" viewBox="0 0 760 320" role="img" aria-label="Baseline and policy scenario trajectory chart" data-chart></svg>
          </div>

          <div class="scar-demo__table-wrap">
            <table class="scar-demo__table">
              <thead><tr><th>Metric</th><th>Baseline</th><th>Policy</th><th>Delta</th><th>Outcome</th></tr></thead>
              <tbody data-comparison-table></tbody>
            </table>
          </div>

          <div class="scar-demo__interpretation">
            <h4>Interpretation notes</h4>
            <ul data-result="notes"></ul>
          </div>

          <div class="scar-demo__actions">
            <button type="button" data-action="copy">Copy comparison</button>
            <button type="button" data-action="download">Download comparison JSON</button>
            <button type="button" data-action="reset">Reset</button>
          </div>
        </div>
      </div>

      <details class="scar-demo__details">
        <summary>What this comparison does and does not do</summary>
        <p>
          This browser demo is an educational companion to Catalyst Analytics R v0.3.0. It now performs a real
          baseline-versus-policy comparison and exports two canonical scenario records plus direction-aware deltas.
          Its simplified browser equations are not numerically identical to the R model. It is not a forecast,
          compliance determination, autonomous recommendation, or substitute for professional analysis.
        </p>
      </details>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
