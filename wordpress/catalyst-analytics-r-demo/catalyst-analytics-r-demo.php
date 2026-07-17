<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for governed data intake and indicator definitions in Catalyst Analytics R.
 * Version: 1.4.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SCAR_DEMO_VERSION', '1.4.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '0.5.0');

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
        <p class="scar-demo__eyebrow">Catalyst Analytics R v0.5.0</p>
        <h3>Validate data and calculate governed indicators</h3>
        <p>
          Paste a tidy CSV dataset, document its source and units, inspect quality flags,
          and calculate a versioned indicator with a complete formula and trace record.
        </p>
      </header>

      <div class="scar-demo__grid">
        <form class="scar-demo__form" data-scar-form>
          <fieldset>
            <legend>Dataset contract</legend>
            <label>Dataset title
              <input type="text" name="datasetTitle" value="Synthetic regional sustainability time series">
            </label>
            <label>Dataset identifier
              <input type="text" name="datasetId" value="sample-country-timeseries">
            </label>
            <label>Source publisher
              <input type="text" name="publisher" value="Content Catalyst LLC">
            </label>
            <label>License or usage statement
              <input type="text" name="license" value="CC0-1.0 synthetic example">
            </label>
            <div class="scar-demo__row">
              <label>Currency code
                <input type="text" name="currency" value="INDEX">
              </label>
              <label>Price year
                <input type="number" name="priceYear" value="2024" min="1900" max="2200">
              </label>
            </div>
          </fieldset>

          <fieldset>
            <legend>Indicator registry</legend>
            <label>Indicator
              <select name="indicator">
                <option value="carbon_intensity">Carbon intensity</option>
                <option value="gdp_per_capita">GDP per capita</option>
                <option value="emissions_per_capita">Emissions per capita</option>
                <option value="adjusted_net_savings">Adjusted net savings</option>
                <option value="cumulative_emissions">Cumulative emissions by region</option>
                <option value="natural_capital_change">Natural-capital change by region</option>
              </select>
            </label>
          </fieldset>

          <fieldset class="scar-demo__data-fieldset">
            <legend>CSV records</legend>
            <p class="scar-demo__hint">Required column names vary by indicator. The sample contains every built-in demonstration field.</p>
            <textarea name="csvData" rows="18" spellcheck="false">year,region,gdp,population,emissions,natural_capital,gross_savings,depreciation,depletion,damages,education_investment
2020,North,100,50,42,92,24,8,4,3,5
2021,North,104,51,41,91,25,8.2,4.1,3.1,5.2
2022,North,109,52,39,91.5,27,8.5,3.9,3.2,5.5
2023,North,115,53,36,92.5,29,8.8,3.5,3,5.9
2024,North,122,54,32,94,32,9.1,3,2.8,6.4
2020,South,80,44,38,85,18,6.5,5,3.5,3.8
2021,South,83,45,37,84,18.5,6.7,5.1,3.6,3.9
2022,South,87,46,36,84.5,19.5,7,4.8,3.7,4.2
2023,South,92,47,34,85.5,21,7.3,4.4,3.5,4.6
2024,South,98,48,31,87,23,7.7,4,3.3,5</textarea>
          </fieldset>
        </form>

        <div class="scar-demo__results" aria-live="polite">
          <div class="scar-demo__scorecards">
            <article><span>Records</span><strong data-result="rows">-</strong><em data-result="dimensions">parsed fields</em></article>
            <article><span>Missing cells</span><strong data-result="missing">-</strong><em>quality check</em></article>
            <article><span>Duplicate keys</span><strong data-result="duplicates">-</strong><em>region plus year</em></article>
            <article><span>Indicator result</span><strong data-result="indicatorSummary">-</strong><em data-result="indicatorUnit">selected definition</em></article>
          </div>

          <div class="scar-demo__definition" data-definition></div>

          <div class="scar-demo__chart-wrap">
            <div class="scar-demo__chart-head">
              <div><h4>Calculated indicator</h4><p>Values are calculated directly from the pasted records and the selected registry definition.</p></div>
            </div>
            <svg class="scar-demo__chart" viewBox="0 0 760 300" role="img" aria-label="Calculated indicator chart" data-chart></svg>
          </div>

          <div class="scar-demo__quality">
            <h4>Data-quality report</h4>
            <ul data-quality-flags></ul>
          </div>

          <div class="scar-demo__table-wrap">
            <table class="scar-demo__table">
              <thead data-table-head></thead>
              <tbody data-table-body></tbody>
            </table>
          </div>

          <div class="scar-demo__trace">
            <h4>Calculation trace</h4>
            <dl data-trace></dl>
          </div>

          <div class="scar-demo__actions">
            <button type="button" data-action="copy">Copy summary</button>
            <button type="button" data-action="download">Download governed JSON</button>
            <button type="button" data-action="reset">Reset sample</button>
          </div>
        </div>
      </div>

      <details class="scar-demo__details">
        <summary>What this data demonstration does and does not do</summary>
        <p>
          The browser validates structure, reports obvious quality issues, and applies transparent indicator formulas.
          It does not verify the truth, license, geographic comparability, currency basis, or methodological suitability of supplied data.
          Publication still requires source and unit review in the R workflow.
        </p>
      </details>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
