<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Connected Sustainability Analytics and Decision Platform companion for Catalyst Analytics R.
 * Version: 3.0.0
 * Author: Content Catalyst LLC
 */
if (!defined('ABSPATH')) { exit; }
define('SCAR_DEMO_VERSION','3.0.0');
function scar_demo_assets(){
  $base=plugin_dir_url(__FILE__);
  wp_enqueue_style('scar-demo',$base.'assets/catalyst-analytics-r-demo.css',array(),SCAR_DEMO_VERSION);
  wp_enqueue_script('scar-demo',$base.'assets/catalyst-analytics-r-demo.js',array(),SCAR_DEMO_VERSION,true);
}
add_action('wp_enqueue_scripts','scar_demo_assets');
function scar_demo_shortcode(){ ob_start(); ?>
<section class="scar-demo" data-scar-demo>
<header class="scar-demo__hero"><p class="scar-demo__eyebrow">Catalyst Analytics R v2.0.0 / WordPress v3.0.0</p><h3>Connected Sustainability Analytics and Decision Platform</h3><p>Map workspaces, evidence, models, decisions, governance, publications, and first-party handoffs into one reviewable analytical graph.</p></header>
<div class="scar-demo__notice"><strong>Connected-platform boundary:</strong> this browser companion maps the contract. It does not execute R, verify identity, persist institutional records, publish artifacts, or authorize decisions.</div>
<form class="scar-demo__form" data-scar-form><div class="scar-demo__controls">
<label><span>Platform title</span><input name="title" value="Sustainable Catalyst Connected Analytics" required></label>
<label><span>Institution</span><input name="institution" value="Sustainable Catalyst" required></label>
<label><span>Workspace</span><input name="workspace" value="Transition Portfolio" required></label>
<label><span>Project</span><input name="project" value="Transition Evidence Project" required></label>
<label><span>Evidence status</span><select name="evidence"><option value="verified">Verified</option><option value="reviewed">Reviewed</option><option value="provisional">Provisional</option><option value="disputed">Disputed</option></select></label>
<label><span>Decision status</span><select name="decision"><option value="in_review">In review</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></label>
<label><span>Publication status</span><select name="publication"><option value="draft">Draft</option><option value="approved">Approved</option><option value="published">Published</option></select></label>
<label><span>Handoff target</span><select name="target"><option value="decision-studio">Decision Studio</option><option value="knowledge-library">Knowledge Library</option><option value="research-lab">Research Lab</option><option value="site-intelligence">Site Intelligence</option></select></label>
</div><div class="scar-demo__actions"><button type="submit">Build connected platform</button><button type="button" class="scar-demo__secondary" data-scar-json>Export canonical JSON</button><button type="button" class="scar-demo__link" data-scar-reset>Reset</button></div></form>
<div class="scar-demo__metrics" role="status" aria-live="polite"><article><span>Nodes</span><strong data-scar-nodes>--</strong></article><article><span>Edges</span><strong data-scar-edges>--</strong></article><article><span>Evidence</span><strong data-scar-evidence>--</strong></article><article><span>Authority</span><strong>Human review</strong></article></div>
<div class="scar-demo__readiness"><strong>Host requirements:</strong> durable storage, authentication, authorization, notifications, transport security, and legally sufficient approval or signature services remain external.</div>
<div class="scar-demo__grid">
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Graph</p><h4>Connected analytical path</h4></div><span class="scar-demo__badge">Contract 2.0.0</span></div><div class="scar-demo__path" data-scar-path></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Lineage</p><h4>Evidence to publication</h4></div></div><div class="scar-demo__ledger" data-scar-lineage></div></article>
<article class="scar-demo__panel"><div class="scar-demo__panel-header"><div><p>Registries</p><h4>Federated records</h4></div></div><div class="scar-demo__checks" data-scar-registries></div></article>
<article class="scar-demo__panel scar-demo__panel--wide"><div class="scar-demo__panel-header"><div><p>Platform connections</p><h4>Governance and handoff</h4></div></div><div class="scar-demo__handoffs" data-scar-handoffs></div></article>
</div></section>
<?php return ob_get_clean(); }
add_shortcode('catalyst_analytics_r_demo','scar_demo_shortcode');
