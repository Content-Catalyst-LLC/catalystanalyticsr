<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Collaborative review and institutional governance companion for Catalyst Analytics R.
 * Version: 2.6.0
 * Author: Content Catalyst LLC
 */
if (!defined('ABSPATH')) { exit; }
function scar_demo_assets() {
  $base = plugin_dir_url(__FILE__);
  wp_enqueue_style('scar-demo', $base . 'assets/catalyst-analytics-r-demo.css', array(), '2.6.0');
  wp_enqueue_script('scar-demo', $base . 'assets/catalyst-analytics-r-demo.js', array(), '2.6.0', true);
}
add_action('wp_enqueue_scripts', 'scar_demo_assets');
function scar_demo_shortcode() { ob_start(); ?>
<section class="scar-demo" data-scar-demo>
<header class="scar-demo__hero"><p class="scar-demo__eyebrow">Catalyst Analytics R v1.6.0 / WordPress v2.6.0</p><h3>Collaborative review and institutional governance</h3><p>Map an analytical project through assignment, structured review, change control, approval, signature, retention, and archival.</p></header>
<div class="scar-demo__notice"><strong>Governance boundary:</strong> this browser companion demonstrates the contract. It does not verify identity, create a legal electronic signature, execute R, or authorize publication.</div>
<form class="scar-demo__form" data-scar-form><div class="scar-demo__controls">
<label><span>Project title</span><input name="title" value="Transition Evidence Project" required></label>
<label><span>Institution</span><input name="institution" value="Sustainable Catalyst" required></label>
<label><span>Classification</span><select name="classification"><option value="internal">Internal</option><option value="confidential">Confidential</option><option value="restricted">Restricted</option><option value="public">Public</option></select></label>
<label><span>Reviewer</span><input name="reviewer" value="Ravi Reviewer" required></label>
<label><span>Review stage</span><select name="stage"><option value="methodology">Methodology</option><option value="analysis">Analysis</option><option value="governance">Governance</option><option value="publication">Publication</option></select></label>
<label><span>Decision</span><select name="decision"><option value="changes_requested">Changes requested</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></label>
<label class="scar-demo__control--wide"><span>Review comment</span><textarea name="comment" rows="3">Document the emissions baseline source and uncertainty range.</textarea></label>
</div><div class="scar-demo__actions"><button type="submit">Build governance preview</button><button type="button" class="scar-demo__secondary" data-scar-json>Export canonical JSON</button><button type="button" class="scar-demo__link" data-scar-reset>Reset</button></div></form>
<div class="scar-demo__metrics" role="status" aria-live="polite"><article><span>Status</span><strong data-scar-status>--</strong></article><article><span>Assignments</span><strong>1</strong></article><article><span>Open changes</span><strong data-scar-changes>--</strong></article><article><span>Authority</span><strong>Human approval</strong></article></div>
<div class="scar-demo__readiness"><strong>Institutional boundary:</strong> the host organization must provide identity, access enforcement, durable storage, notifications, and any legally required signature service.</div>
<div class="scar-demo__grid">
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Workflow</p><h4>Review and approval path</h4></div><span class="scar-demo__badge">Contract 1.0.0</span></div><div class="scar-demo__path" data-scar-path></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Assignment</p><h4>Reviewer record</h4></div></div><div class="scar-demo__ledger" data-scar-ledger></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Controls</p><h4>Access and retention</h4></div></div><div class="scar-demo__checks" data-scar-controls></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Audit</p><h4>Governance events</h4></div></div><div class="scar-demo__handoffs" data-scar-audit></div></article>
</div></section>
<?php return ob_get_clean(); }
add_shortcode('catalyst_analytics_r_demo','scar_demo_shortcode');
