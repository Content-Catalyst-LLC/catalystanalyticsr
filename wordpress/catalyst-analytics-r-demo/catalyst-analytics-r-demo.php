<?php
/**
 * Plugin Name: Catalyst Analytics R Demo
 * Description: Browser companion for saved analytical workspaces, reusable scenario libraries, project comparison, snapshots, and workspace export.
 * Version: 2.1.0
 * Author: Content Catalyst LLC
 * License: MIT
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SCAR_DEMO_VERSION', '2.1.0');
define('SCAR_COMPATIBLE_REPOSITORY_VERSION', '1.1.0');

function scar_demo_assets() {
    $base = plugin_dir_url(__FILE__);
    wp_enqueue_style('catalyst-analytics-r-demo', $base . 'assets/catalyst-analytics-r-demo.css', array(), SCAR_DEMO_VERSION);
    wp_enqueue_script('catalyst-analytics-r-demo', $base . 'assets/catalyst-analytics-r-demo.js', array(), SCAR_DEMO_VERSION, true);
}
add_action('wp_enqueue_scripts', 'scar_demo_assets');

function scar_demo_shortcode() {
    ob_start();
    ?>
    <section class="scar-demo" data-scar-demo>
      <header class="scar-demo__header">
        <p class="scar-demo__eyebrow">Catalyst Analytics R v1.1.0</p>
        <h3>Saved workspace and scenario library</h3>
        <p>Organize multiple analytical projects, reusable scenarios, parameter sets, policy packages, run history, and version snapshots inside one portable workspace contract.</p>
      </header>

      <div class="scar-demo__notice"><strong>Educational browser companion.</strong> This interface maps to the v1.1.0 workspace contract. It does not execute R, persist data on the server, validate model fitness, or authorize decisions.</div>

      <form class="scar-demo__form" data-scar-form>
        <div class="scar-demo__controls">
          <label><span>Workspace title</span><input type="text" name="workspaceTitle" value="Transition Analytics Workspace" required></label>
          <label><span>Workspace id</span><input type="text" name="workspaceId" value="transition-workspace" pattern="[A-Za-z0-9._-]+" required></label>
          <label><span>Owner</span><input type="text" name="owner" value="Sustainable Catalyst"></label>
          <label><span>Active project</span><select name="activeProject"><option value="transition-evidence">Transition evidence</option><option value="regional-pathway">Regional pathway</option></select></label>
          <label><span>Baseline savings rate</span><input type="number" name="baselineSavings" min="0.05" max="0.60" step="0.01" value="0.18"></label>
          <label><span>Transition savings rate</span><input type="number" name="policySavings" min="0.05" max="0.60" step="0.01" value="0.25"></label>
          <label><span>Baseline emissions intensity</span><input type="number" name="baselineEmissions" min="0.01" max="1" step="0.01" value="0.30"></label>
          <label><span>Transition emissions intensity</span><input type="number" name="policyEmissions" min="0.01" max="1" step="0.01" value="0.14"></label>
          <label class="scar-demo__control--wide"><span>Workspace purpose</span><textarea name="description" rows="3">Compare reusable transition pathways across projects while preserving runs, review status, and restoration points.</textarea></label>
        </div>
        <div class="scar-demo__actions">
          <button type="submit">Build workspace</button>
          <button type="button" class="scar-demo__secondary" data-scar-clone>Clone transition scenario</button>
          <button type="button" class="scar-demo__secondary" data-scar-snapshot>Create snapshot</button>
          <button type="button" class="scar-demo__secondary" data-scar-json>Export workspace JSON</button>
          <button type="button" class="scar-demo__link" data-scar-reset>Reset</button>
        </div>
      </form>

      <div class="scar-demo__metrics" role="status" aria-live="polite">
        <article><span>Workspace fingerprint</span><strong data-scar-fingerprint>--</strong></article>
        <article><span>Projects</span><strong data-scar-projects>--</strong></article>
        <article><span>Scenario library</span><strong data-scar-scenarios>--</strong></article>
        <article><span>Snapshots</span><strong data-scar-snapshots>--</strong></article>
      </div>

      <div class="scar-demo__readiness"><strong>Stable workspace contract:</strong> projects remain independent analytical records; libraries preserve reusable inputs; snapshots preserve restoration points; exports are explicit and portable.</div>

      <div class="scar-demo__grid">
        <article class="scar-demo__panel scar-demo__panel--wide">
          <div class="scar-demo__panel-header"><div><p>Workspace map</p><h4>Projects, libraries, history, and snapshots</h4></div><span class="scar-demo__badge">Contract 1.0.0</span></div>
          <div class="scar-demo__path" data-scar-path></div>
        </article>
        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Project library</p><h4>Saved analytical projects</h4></div></div>
          <div class="scar-demo__ledger" data-scar-project-list></div>
        </article>
        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Scenario library</p><h4>Reusable pathways</h4></div></div>
          <div class="scar-demo__ledger" data-scar-scenario-list></div>
        </article>
        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Run history</p><h4>Cross-project records</h4></div></div>
          <div class="scar-demo__checks" data-scar-run-history></div>
        </article>
        <article class="scar-demo__panel">
          <div class="scar-demo__panel-header"><div><p>Reusable package</p><h4>Policy and parameters</h4></div></div>
          <div class="scar-demo__artifacts" data-scar-package></div>
        </article>
        <article class="scar-demo__panel scar-demo__panel--wide">
          <div class="scar-demo__panel-header"><div><p>Version history</p><h4>Workspace restoration points</h4></div><span class="scar-demo__badge" data-scar-active>--</span></div>
          <div class="scar-demo__handoffs" data-scar-snapshot-list></div>
        </article>
      </div>
    </section>
    <?php
    return ob_get_clean();
}
add_shortcode('catalyst_analytics_r_demo', 'scar_demo_shortcode');
