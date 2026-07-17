# Optimization and Policy Pathway Design

Catalyst Analytics R v1.3.0 adds a governed analytical layer for exploring policy choices without transferring decision authority to software.

## Optimization contract

The optimization engine separates:

- decision variables and their scenario targets;
- objective metrics, directions, targets, and weights;
- hard and soft feasibility constraints;
- candidate generation and evaluator execution;
- feasible-region, objective-score, and Pareto diagnostics;
- one unreviewed recommendation selected from feasible candidates.

Grid and reproducible random-search methods are included. Evaluators remain user-supplied analytical functions, so the package does not claim that an optimized result is causally valid.

## Target-seeking scenarios

A selected candidate can be mapped back into a canonical scenario through declared nested targets such as `policy$e` or `parameters$alpha`. The resulting scenario retains the optimization record and remains an intervention draft requiring review.

## Economic and abatement evidence

Cost-effectiveness analysis preserves incremental costs, incremental effects, dominated options, and incremental cost-effectiveness ratios. Marginal-abatement analysis preserves option-level costs, abatement quantities, costs per unit, and cumulative abatement.

## Adaptive pathways

Policy pathways contain ordered stages, planned actions, human decision gates, and evidence triggers. Trigger evaluation produces review prompts only. It never executes an action.

## Robustness

Pathway robustness is assessed across declared futures using normalized objective loss and regret. Low regret does not establish prediction accuracy; it indicates relative performance within the supplied scenarios and metrics.

## Publication boundary

Every optimization and pathway export states that:

- human review is required;
- a recommendation is not authorization;
- an adaptive trigger is not execution;
- evaluator and causal validity are not established by optimization alone.
