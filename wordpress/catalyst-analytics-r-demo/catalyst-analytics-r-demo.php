<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser-based Sustainable Catalyst analytics demo for scenario exploration, emissions budget review, and adjusted-net-savings style reasoning. Use shortcode [catalyst_analytics_r_demo].
 * Version: 1.1.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

function scar_demo_enqueue_assets() {
    $url = plugin_dir_url(__FILE__);
    $ver = '1.1.0';
    wp_enqueue_style('scar-demo-style', $url . 'assets/catalyst-analytics-r-demo.css', array(), $ver);
    wp_enqueue_script('scar-demo-script', $url . 'assets/catalyst-analytics-r-demo.js', array(), $ver, true);
}

function scar_demo_shortcode($atts = array(), $content = null) {
    scar_demo_enqueue_assets();
    ob_start();
    ?>
    <div class="scar-demo" data-scar-demo>
      <div class="scar-demo__header">
        <p class="scar-demo__eyebrow">Catalyst Analytics R Demo</p>
        <h3>Scenario Engine for Sustainable-Development Analysis</h3>
        <p>
          Explore one policy scenario using simplified browser-side logic mapped to the Catalyst Analytics R canonical scenario contract.
          Adjust savings, emissions intensity, adaptation investment, restoration, and social investment to see how trajectory,
          adjusted-net-savings style indicators, and emissions-budget status change.
        </p>
      </div>

      <div class="scar-demo__grid">
        <form class="scar-demo__form" data-scar-form>
          <fieldset>
            <legend>Scenario setup</legend>
            <label>
              Scenario name
              <input type="text" name="scenarioName" value="Policy pathway" maxlength="80">
            </label>
            <label>
              Time horizon <span data-out="yearsOut">20 years</span>
              <input type="range" name="years" min="5" max="40" step="1" value="20">
            </label>
          </fieldset>

          <fieldset>
            <legend>Policy controls</legend>
            <label>
              Savings / reinvestment rate <span data-out="savingsOut">22%</span>
              <input type="range" name="savings" min="5" max="45" step="1" value="22">
            </label>
            <label>
              Emissions intensity <span data-out="emissionsOut">7%</span>
              <input type="range" name="emissionsIntensity" min="1" max="20" step="1" value="7">
            </label>
            <label>
              Adaptation / resilience investment <span data-out="adaptOut">8%</span>
              <input type="range" name="adaptation" min="0" max="25" step="1" value="8">
            </label>
            <label>
              Natural-capital restoration <span data-out="restoreOut">6%</span>
              <input type="range" name="restoration" min="0" max="20" step="1" value="6">
            </label>
            <label>
              Human / social investment <span data-out="humanOut">5%</span>
              <input type="range" name="humanInvestment" min="0" max="20" step="1" value="5">
            </label>
          </fieldset>

          <fieldset>
            <legend>Initial conditions and budget</legend>
            <label>
              Initial produced capital
              <input type="number" name="initialCapital" min="10" max="1000" step="10" value="100">
            </label>
            <label>
              Initial human capital
              <input type="number" name="initialHuman" min="10" max="1000" step="10" value="100">
            </label>
            <label>
              Initial natural capital
              <input type="number" name="initialNatural" min="10" max="1000" step="10" value="100">
            </label>
            <label>
              Emissions budget
              <input type="number" name="emissionsBudget" min="10" max="1000" step="10" value="120">
            </label>
          </fieldset>
        </form>

        <div class="scar-demo__results" aria-live="polite">
          <div class="scar-demo__scorecards">
            <article>
              <span>Composite score</span>
              <strong data-result="score">—</strong>
              <em data-result="scoreNote">Awaiting calculation</em>
            </article>
            <article>
              <span>Adjusted savings</span>
              <strong data-result="ans">—</strong>
              <em>final-period estimate</em>
            </article>
            <article>
              <span>Budget status</span>
              <strong data-result="budget">—</strong>
              <em data-result="budgetNote">cumulative emissions</em>
            </article>
          </div>

          <div class="scar-demo__chart-wrap">
            <div class="scar-demo__chart-head">
              <h4>Trajectory summary</h4>
              <p>Produced capital, human capital, natural capital, and cumulative emissions.</p>
            </div>
            <svg class="scar-demo__chart" viewBox="0 0 720 300" role="img" aria-label="Scenario trajectory chart" data-chart></svg>
          </div>

          <div class="scar-demo__interpretation">
            <h4>Interpretation notes</h4>
            <ul data-result="notes"></ul>
          </div>

          <div class="scar-demo__actions">
            <button type="button" data-action="copy">Copy summary</button>
            <button type="button" data-action="download">Download JSON</button>
            <button type="button" data-action="reset">Reset</button>
          </div>
        </div>
      </div>

      <details class="scar-demo__details">
        <summary>What this demo does and does not do</summary>
        <p>
          This browser demo is a simplified educational companion to Catalyst Analytics R v0.2.0. Its exports now include a canonical scenario record. Its equations remain conceptually related but are not numerically identical to the R engine. It is not a full R runtime,
          not a forecast, not compliance advice, and not a guarantee of impact. Use it to understand scenario structure,
          assumptions, indicators, and reviewable exports.
        </p>
      </details>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
