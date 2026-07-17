<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Comparative uncertainty demo for baseline-versus-policy scenario analysis, ensemble intervals, probability review, stress signals, and canonical Catalyst Analytics R exports. Use shortcode [catalyst_analytics_r_demo].
 * Version: 1.3.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

function scar_demo_enqueue_assets() {
    $url = plugin_dir_url(__FILE__);
    $ver = '1.3.0';
    wp_enqueue_style('scar-demo-style', $url . 'assets/catalyst-analytics-r-demo.css', array(), $ver);
    wp_enqueue_script('scar-demo-script', $url . 'assets/catalyst-analytics-r-demo.js', array(), $ver, true);
}

function scar_demo_shortcode($atts = array(), $content = null) {
    scar_demo_enqueue_assets();
    ob_start();
    ?>
    <div class="scar-demo" data-scar-demo>
      <div class="scar-demo__header">
        <p class="scar-demo__eyebrow">Catalyst Analytics R Uncertainty Demo</p>
        <h3>Compare pathways under declared uncertainty</h3>
        <p>
          Compare a baseline with a policy pathway, then run a reproducible browser ensemble around the policy assumptions.
          Review P10-P90 intervals, emissions-budget probability, sensitivity signals, and a canonical export mapped to Catalyst Analytics R v0.4.0.
        </p>
      </div>

      <div class="scar-demo__grid">
        <form class="scar-demo__form" data-scar-form>
          <fieldset>
            <legend>Shared scope</legend>
            <label>Time horizon <span data-out="yearsOut">20 years</span><input type="range" name="years" min="5" max="40" step="1" value="20"></label>
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

          <fieldset class="scar-demo__uncertainty">
            <legend>Policy uncertainty</legend>
            <label>Sampling design
              <select name="sampling"><option value="latin_hypercube">Latin hypercube</option><option value="monte_carlo">Monte Carlo</option></select>
            </label>
            <label>Realizations
              <select name="simulations"><option value="100">100</option><option value="250" selected>250</option><option value="500">500</option></select>
            </label>
            <label>Seed <input type="number" name="seed" min="1" max="999999" step="1" value="42"></label>
            <label>Emissions-intensity range <span data-out="emissionsWidthOut">+/- 30%</span><input type="range" name="emissionsWidth" min="0" max="80" step="5" value="30"></label>
            <label>Restoration range <span data-out="restorationWidthOut">+/- 25%</span><input type="range" name="restorationWidth" min="0" max="80" step="5" value="25"></label>
            <label>Adaptation range <span data-out="adaptationWidthOut">+/- 20%</span><input type="range" name="adaptationWidth" min="0" max="80" step="5" value="20"></label>
          </fieldset>
        </form>

        <div class="scar-demo__results" aria-live="polite">
          <div class="scar-demo__scorecards">
            <article><span>Composite-score delta</span><strong data-result="scoreDelta">-</strong><em data-result="scoreNote">policy versus baseline</em></article>
            <article><span>Policy budget probability</span><strong data-result="budgetProbability">-</strong><em data-result="budgetNote">ensemble realizations</em></article>
            <article><span>Policy score P10-P90</span><strong data-result="scoreInterval">-</strong><em>uncertainty interval</em></article>
            <article><span>Strongest sensitivity</span><strong data-result="sensitivity">-</strong><em data-result="sensitivityNote">rank-correlation signal</em></article>
          </div>

          <div class="scar-demo__chart-wrap">
            <div class="scar-demo__chart-head">
              <div><h4>Policy uncertainty band</h4><p>Baseline, median policy pathway, and the policy P10-P90 envelope.</p></div>
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
            <svg class="scar-demo__chart" viewBox="0 0 760 320" role="img" aria-label="Baseline and policy uncertainty trajectory chart" data-chart></svg>
          </div>

          <div class="scar-demo__table-wrap">
            <table class="scar-demo__table">
              <thead><tr><th>Metric</th><th>Baseline</th><th>Policy median</th><th>P10</th><th>P90</th><th>Outcome</th></tr></thead>
              <tbody data-uncertainty-table></tbody>
            </table>
          </div>

          <div class="scar-demo__interpretation"><h4>Interpretation notes</h4><ul data-result="notes"></ul></div>

          <div class="scar-demo__actions">
            <button type="button" data-action="copy">Copy analysis</button>
            <button type="button" data-action="download">Download uncertainty JSON</button>
            <button type="button" data-action="reset">Reset</button>
          </div>
        </div>
      </div>

      <details class="scar-demo__details">
        <summary>What this uncertainty analysis does and does not do</summary>
        <p>
          This educational browser companion performs a real seeded ensemble and reports declared-assumption uncertainty.
          Its simplified equations are not numerically identical to the R engine, and its probabilities are not empirical forecasts.
          It is not a compliance determination, autonomous recommendation, or substitute for professional analysis.
        </p>
      </details>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
