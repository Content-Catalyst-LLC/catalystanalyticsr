<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for regional, sector, and portfolio analytics, weighted indicators, carbon budgets, and transition pathways.
 * Version: 2.2.0
 * Author: Content Catalyst LLC
 * License: MIT
 */
if (!defined('ABSPATH')) { exit; }
define('SCAR_DEMO_VERSION', '2.2.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '1.2.0');
function scar_demo_assets() { $base=plugin_dir_url(__FILE__); wp_enqueue_style('catalyst-analytics-r-demo',$base.'assets/catalyst-analytics-r-demo.css',array(),SCAR_DEMO_VERSION); wp_enqueue_script('catalyst-analytics-r-demo',$base.'assets/catalyst-analytics-r-demo.js',array(),SCAR_DEMO_VERSION,true); }
add_action('wp_enqueue_scripts','scar_demo_assets');
function scar_demo_shortcode() { ob_start(); ?>
<section class="scar-demo" data-scar-demo>
<header class="scar-demo__header"><p class="scar-demo__eyebrow">Catalyst Analytics R v1.2.0</p><h3>Regional, sector, and portfolio analytics</h3><p>Compare weighted regional portfolios, carbon-budget pathways, and sector transition performance inside a governed analytical contract.</p></header>
<div class="scar-demo__notice"><strong>Educational browser companion.</strong> This interface maps to the v1.2.0 contracts. It does not execute R, validate causal claims, allocate budgets, or authorize policy decisions.</div>
<form class="scar-demo__form" data-scar-form><div class="scar-demo__controls">
<label><span>Portfolio title</span><input name="title" value="Regional Transition Portfolio" required></label>
<label><span>Northern weight</span><input type="number" name="northWeight" value="60" min="0" step="1"></label>
<label><span>Southern weight</span><input type="number" name="southWeight" value="40" min="0" step="1"></label>
<label><span>Northern GDP index</span><input type="number" name="northGdp" value="120" step="1"></label>
<label><span>Southern GDP index</span><input type="number" name="southGdp" value="90" step="1"></label>
<label><span>Northern annual emissions</span><input type="number" name="northEmissions" value="18" step="0.1"></label>
<label><span>Southern annual emissions</span><input type="number" name="southEmissions" value="11" step="0.1"></label>
<label><span>Northern carbon budget</span><input type="number" name="northBudget" value="50" step="1"></label>
<label><span>Southern carbon budget</span><input type="number" name="southBudget" value="40" step="1"></label>
</div><div class="scar-demo__actions"><button type="submit">Run portfolio analysis</button><button type="button" class="scar-demo__secondary" data-scar-json>Export canonical JSON</button><button type="button" class="scar-demo__link" data-scar-reset>Reset</button></div></form>
<div class="scar-demo__metrics" role="status" aria-live="polite"><article><span>Weighted GDP</span><strong data-scar-gdp>--</strong></article><article><span>Weighted emissions</span><strong data-scar-emissions>--</strong></article><article><span>Budget status</span><strong data-scar-budget>--</strong></article><article><span>Transition status</span><strong data-scar-transition>--</strong></article></div>
<div class="scar-demo__readiness"><strong>Review boundary:</strong> regional comparability requires consistent units and sources; weights are analytical assumptions, not allocation authority.</div>
<div class="scar-demo__grid">
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Portfolio map</p><h4>Regions, sectors, indicators, and pathways</h4></div><span class="scar-demo__badge">Contract 1.0.0</span></div><div class="scar-demo__path" data-scar-path></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Regional comparison</p><h4>Weighted members</h4></div></div><div class="scar-demo__ledger" data-scar-regions></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Carbon budgets</p><h4>Remaining allocation</h4></div></div><div class="scar-demo__checks" data-scar-budgets></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Sector pathways</p><h4>Output and emissions decoupling</h4></div></div><div class="scar-demo__handoffs" data-scar-sectors></div></article>
</div></section>
<?php return ob_get_clean(); }
add_shortcode('catalyst_analytics_r_demo','scar_demo_shortcode');
