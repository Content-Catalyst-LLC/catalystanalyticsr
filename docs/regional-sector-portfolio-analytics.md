# Regional, Sector, and Portfolio Analytics

Catalyst Analytics R v1.2.0 adds governed spatial and sector scope records, weighted portfolio aggregation, regional ranking, carbon-budget allocation diagnostics, and sector transition pathways.

## Scope contracts

`geography_scope()` records stable identifiers, hierarchy, external codes, and metadata. `sector_scope()` records classification systems, codes, and parent sectors. `scope_scenario()` applies these records to the canonical scenario contract without changing the underlying model equations.

## Portfolio contract

A regional portfolio is a reviewable collection of members. Each member has one geography, one or more sectors, a non-negative analytical weight, governed indicator records, and an optional carbon-budget allocation. Weights support analytical aggregation only; they do not authorize funding, policy, or resource allocation.

## Carbon budgets

`regional_carbon_budgets()` calculates annual and cumulative emissions, remaining budget, budget share used, and first overshoot period for each geography. Units and geography identifiers must be consistent before comparison.

## Sector transitions

`sector_transition_pathways()` compares output, emissions, and emissions intensity between the first and last observation. It distinguishes absolute decoupling, improving intensity, and transition gaps.

## Publication

`export_regional_portfolio_analysis()` writes the complete portfolio, weighted indicator tables, regional comparisons, carbon diagnostics, sector pathways, a human-readable brief, and an integrity manifest.
