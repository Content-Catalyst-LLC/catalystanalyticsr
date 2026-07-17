<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for optimization, Pareto trade-offs, target-seeking scenarios, and adaptive policy pathways.
 * Version: 2.3.0
 * Author: Content Catalyst LLC
 * License: MIT
 */
if (!defined('ABSPATH')) { exit; }
define('SCAR_DEMO_VERSION', '2.3.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '1.3.0');
function scar_demo_assets() { $base=plugin_dir_url(__FILE__); wp_enqueue_style('catalyst-analytics-r-demo',$base.'assets/catalyst-analytics-r-demo.css',array(),SCAR_DEMO_VERSION); wp_enqueue_script('catalyst-analytics-r-demo',$base.'assets/catalyst-analytics-r-demo.js',array(),SCAR_DEMO_VERSION,true); }
add_action('wp_enqueue_scripts','scar_demo_assets');
function scar_demo_shortcode() { ob_start(); ?>
<section class="scar-demo" data-scar-demo>
<header class="scar-demo__header"><p class="scar-demo__eyebrow">Catalyst Analytics R v1.3.0</p><h3>Optimization and policy pathway design</h3><p>Explore feasible policy regions, Pareto trade-offs, target-seeking choices, and staged adaptive pathways inside a governed analytical contract.</p></header>
<div class="scar-demo__notice"><strong>Educational browser companion.</strong> This interface maps to v1.3.0 contracts. It does not execute R, establish causal validity, authorize policy, allocate resources, or execute adaptive triggers.</div>
<form class="scar-demo__form" data-scar-form><div class="scar-demo__controls">
<label><span>Analysis title</span><input name="title" value="Transition Policy Design" required></label>
<label><span>Emissions target</span><input type="number" name="emissionsTarget" value="70" step="1"></label>
<label><span>Maximum cost</span><input type="number" name="maximumCost" value="205" step="1"></label>
<label><span>Jobs floor</span><input type="number" name="jobsFloor" value="48" step="1"></label>
<label><span>Emissions weight</span><input type="number" name="emissionsWeight" value="65" min="0" max="100" step="5"></label>
<label><span>Cost weight</span><input type="number" name="costWeight" value="35" min="0" max="100" step="5"></label>
</div><div class="scar-demo__actions"><button type="submit">Optimize policy pathway</button><button type="button" class="scar-demo__secondary" data-scar-json>Export canonical JSON</button><button type="button" class="scar-demo__link" data-scar-reset>Reset</button></div></form>
<div class="scar-demo__metrics" role="status" aria-live="polite"><article><span>Feasible candidates</span><strong data-scar-feasible>--</strong></article><article><span>Pareto frontier</span><strong data-scar-pareto>--</strong></article><article><span>Recommended levers</span><strong data-scar-recommendation>--</strong></article><article><span>Review status</span><strong data-scar-review>Human review</strong></article></div>
<div class="scar-demo__readiness"><strong>Decision boundary:</strong> optimization narrows choices; it does not make decisions. Adaptive triggers create review prompts and never execute actions.</div>
<div class="scar-demo__grid">
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Analytical path</p><h4>Variables, constraints, trade-offs, and review</h4></div><span class="scar-demo__badge">Contract 1.0.0</span></div><div class="scar-demo__path" data-scar-path></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Recommendation</p><h4>Target-seeking candidate</h4></div></div><div class="scar-demo__ledger" data-scar-ledger></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Feasible region</p><h4>Constraint diagnostics</h4></div></div><div class="scar-demo__checks" data-scar-checks></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Pareto frontier</p><h4>Non-dominated cost and emissions choices</h4></div></div><div class="scar-demo__pareto" data-scar-pareto-list></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Adaptive pathway</p><h4>Stages, decision gates, and trigger prompts</h4></div></div><div class="scar-demo__handoffs" data-scar-stages></div></article>
</div></section>
<?php return ob_get_clean(); }
add_shortcode('catalyst_analytics_r_demo','scar_demo_shortcode');
