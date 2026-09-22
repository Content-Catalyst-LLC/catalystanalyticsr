\name{uncertainty_sensitivity_runtime_manifest}
\alias{uncertainty_sensitivity_runtime_manifest}
\alias{uncertainty_sensitivity_runtime_request}
\alias{validate_uncertainty_sensitivity_runtime_request}
\alias{run_uncertainty_sensitivity_runtime}
\alias{morris_sensitivity}
\alias{sobol_sensitivity}
\alias{uncertainty_sensitivity_evidence_bundle}
\alias{validate_uncertainty_sensitivity_evidence_bundle}
\alias{uncertainty_sensitivity_to_json}
\alias{uncertainty_sensitivity_from_json}
\title{Bounded uncertainty and sensitivity runtime}
\description{
Defines the Catalyst Analytics R v2.3.0 bounded uncertainty and sensitivity runtime used by Workspace and Platform Core integration.
}
\usage{
uncertainty_sensitivity_runtime_manifest()

uncertainty_sensitivity_runtime_request(
  scenario,
  method = c("monte_carlo", "latin_hypercube", "morris", "sobol"),
  n = 256L,
  seed = 42L,
  metrics = NULL,
  thresholds = list(),
  integration_method = NULL,
  morris_delta = 0.1,
  max_evaluations = 20000L,
  continue_on_error = TRUE
)

morris_sensitivity(
  scenario,
  n = 32L,
  seed = 42L,
  metrics = NULL,
  delta = 0.1,
  integration_method = NULL,
  max_evaluations = 20000L
)

sobol_sensitivity(
  scenario,
  n = 128L,
  seed = 42L,
  metrics = NULL,
  integration_method = NULL,
  max_evaluations = 20000L
)

run_uncertainty_sensitivity_runtime(request)
}
\arguments{
\item{scenario}{Canonical Catalyst scenario.}
\item{method}{Governed runtime method.}
\item{n}{Sample or base-design size.}
\item{seed}{Reproducible seed.}
\item{metrics}{Terminal indicator names.}
\item{thresholds}{Probability rules for ensembles.}
\item{integration_method}{Registered scenario integration method.}
\item{morris_delta}{Morris perturbation.}
\item{delta}{Morris perturbation.}
\item{max_evaluations}{Evaluation budget.}
\item{continue_on_error}{Whether ensemble failures are recorded and skipped.}
\item{request}{Validated runtime request.}
}
\value{
A runtime manifest, request, structured sensitivity result, or Core-ready evidence bundle.
}
\details{
Remote callers cannot supply arbitrary R functions. Uncertainty and sensitivity are evidence and require human interpretation.
}
\keyword{models}
