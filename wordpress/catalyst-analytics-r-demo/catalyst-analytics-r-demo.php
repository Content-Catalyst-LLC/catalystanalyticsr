<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for governed econometrics, difference-in-differences, event studies, synthetic controls, and causal-assumption review.
 * Version: 2.4.0
 * Author: Content Catalyst LLC
 * License: MIT
 */
if (!defined('ABSPATH')) { exit; }
define('SCAR_DEMO_VERSION', '2.4.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '1.4.0');
function scar_demo_assets() { $base=plugin_dir_url(__FILE__); wp_enqueue_style('catalyst-analytics-r-demo',$base.'assets/catalyst-analytics-r-demo.css',array(),SCAR_DEMO_VERSION); wp_enqueue_script('catalyst-analytics-r-demo',$base.'assets/catalyst-analytics-r-demo.js',array(),SCAR_DEMO_VERSION,true); }
add_action('wp_enqueue_scripts','scar_demo_assets');
function scar_demo_shortcode() { ob_start(); ?>
<section class="scar-demo" data-scar-demo>
<header class="scar-demo__header"><p class="scar-demo__eyebrow">Catalyst Analytics R v1.4.0</p><h3>Econometrics and policy evaluation</h3><p>Explore difference-in-differences, event-study dynamics, synthetic controls, uncertainty, and explicit causal-assumption review.</p></header>
<div class="scar-demo__notice"><strong>Educational browser companion.</strong> This interface maps to v1.4.0 contracts. It does not execute R, prove causality, authorize policy, or replace identification and domain review.</div>
<form class="scar-demo__form" data-scar-form><div class="scar-demo__controls">
<label><span>Analysis title</span><input name="title" value="Transition Policy Evaluation" required></label>
<label><span>True policy effect</span><input type="number" name="effect" value="-8" step="0.5"></label>
<label><span>Baseline trend</span><input type="number" name="trend" value="2" step="0.25"></label>
<label><span>Intervention period</span><input type="number" name="intervention" value="4" min="3" max="6" step="1"></label>
<label><span>Noise scale</span><input type="number" name="noise" value="1" min="0" max="5" step="0.25"></label>
<label><span>Confidence level</span><select name="confidence"><option value="0.90">90%</option><option value="0.95" selected>95%</option><option value="0.99">99%</option></select></label>
</div><div class="scar-demo__actions"><button type="submit">Evaluate policy effect</button><button type="button" class="scar-demo__secondary" data-scar-json>Export canonical JSON</button><button type="button" class="scar-demo__link" data-scar-reset>Reset</button></div></form>
<div class="scar-demo__metrics" role="status" aria-live="polite"><article><span>Difference-in-differences</span><strong data-scar-did>--</strong></article><article><span>Synthetic-control gap</span><strong data-scar-synth>--</strong></article><article><span>Pretrend status</span><strong data-scar-pretrend>--</strong></article><article><span>Review status</span><strong>Human review</strong></article></div>
<div class="scar-demo__readiness"><strong>Causal boundary:</strong> estimates are conditional on parallel trends, no interference, timing, functional-form, and support assumptions.</div>
<div class="scar-demo__grid">
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Evaluation path</p><h4>Data, design, diagnostics, effects, and review</h4></div><span class="scar-demo__badge">Contract 1.0.0</span></div><div class="scar-demo__path" data-scar-path></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Policy effects</p><h4>Estimate ledger</h4></div></div><div class="scar-demo__ledger" data-scar-ledger></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Identification</p><h4>Assumption review</h4></div></div><div class="scar-demo__checks" data-scar-assumptions></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Event study</p><h4>Dynamic treatment effects</h4></div></div><div class="scar-demo__pareto" data-scar-event></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Method evidence</p><h4>Regression, panel, and synthetic-control diagnostics</h4></div></div><div class="scar-demo__handoffs" data-scar-methods></div></article>
</div></section>
<?php return ob_get_clean(); }
add_shortcode('catalyst_analytics_r_demo','scar_demo_shortcode');
