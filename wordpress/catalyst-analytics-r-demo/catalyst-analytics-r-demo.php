<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Public API and Sustainable Catalyst handoff companion for Catalyst Analytics R.
 * Version: 2.5.0
 * Author: Content Catalyst LLC
 */
if (!defined('ABSPATH')) { exit; }
function scar_demo_assets() {
  $base = plugin_dir_url(__FILE__);
  wp_enqueue_style('scar-demo', $base . 'assets/catalyst-analytics-r-demo.css', array(), '2.5.0');
  wp_enqueue_script('scar-demo', $base . 'assets/catalyst-analytics-r-demo.js', array(), '2.5.0', true);
}
add_action('wp_enqueue_scripts', 'scar_demo_assets');
function scar_demo_shortcode() { ob_start(); ?>
<section class="scar-demo" data-scar-demo>
<header class="scar-demo__hero"><p class="scar-demo__eyebrow">Catalyst Analytics R v1.5.0 / WordPress v2.5.0</p><h3>Public API and platform handoffs</h3><p>Inspect the versioned API surface and assemble a governed handoff for a Sustainable Catalyst product.</p></header>
<div class="scar-demo__notice"><strong>Execution boundary:</strong> this browser companion maps the public contract. It does not execute R, collect credentials, call private APIs, or authorize actions in another product.</div>
<form class="scar-demo__form" data-scar-form><div class="scar-demo__controls">
<label><span>Project title</span><input name="title" value="Transition Evidence Project" required></label>
<label><span>Target product</span><select name="target"><option value="site_intelligence">Site Intelligence</option><option value="research_lab">Research Lab</option><option value="workbench">Workbench</option><option value="catalyst_canvas">Catalyst Canvas</option><option value="decision_studio">Decision Studio</option><option value="knowledge_library">Knowledge Library</option></select></label>
<label><span>Geographic scope</span><input name="geography" value="WORLD"></label>
<label><span>Primary indicator</span><input name="indicator" value="emissions"></label>
<label><span>Review status</span><select name="review"><option value="requires_review">Requires review</option><option value="reviewed">Reviewed</option><option value="approved">Approved for transfer</option></select></label>
</div><div class="scar-demo__actions"><button type="submit">Build handoff preview</button><button type="button" class="scar-demo__secondary" data-scar-json>Export canonical JSON</button><button type="button" class="scar-demo__link" data-scar-reset>Reset</button></div></form>
<div class="scar-demo__metrics" role="status" aria-live="polite"><article><span>API version</span><strong>v1</strong></article><article><span>Endpoint count</span><strong data-scar-endpoints>9</strong></article><article><span>Target</span><strong data-scar-target>--</strong></article><article><span>Authority</span><strong>Human review</strong></article></div>
<div class="scar-demo__readiness"><strong>Platform boundary:</strong> the receiving product must validate the contract, preserve provenance and licenses, and obtain any required approval.</div>
<div class="scar-demo__grid">
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Public API</p><h4>Versioned endpoint manifest</h4></div><span class="scar-demo__badge">Contract 1.0.0</span></div><div class="scar-demo__path" data-scar-path></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Handoff</p><h4>Transfer record</h4></div></div><div class="scar-demo__ledger" data-scar-ledger></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Review</p><h4>Required safeguards</h4></div></div><div class="scar-demo__checks" data-scar-boundaries></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Target payload</p><h4>Product-specific content</h4></div></div><div class="scar-demo__handoffs" data-scar-payload></div></article>
</div></section>
<?php return ob_get_clean(); }
add_shortcode('catalyst_analytics_r_demo','scar_demo_shortcode');
