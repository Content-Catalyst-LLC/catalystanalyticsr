\name{uncertainty_engine}
\alias{uncertainty_spec}
\alias{validate_uncertainty_spec}
\alias{sample_uncertainty}
\alias{run_uncertainty}
\alias{uncertainty_summary}
\alias{uncertainty_probabilities}
\alias{global_sensitivity}
\alias{local_sensitivity}
\alias{plot_uncertainty}
\alias{plot_tornado}
\alias{stress_shock}
\alias{stress_case}
\alias{run_stress_tests}
\alias{stress_test_summary}
\alias{plot_stress_test}
\title{Uncertainty, sensitivity, and stress testing}
\description{Defines governed uncertainty distributions, samples scenario ensembles, summarizes uncertainty and sensitivity, and evaluates named stress cases.}
\usage{
uncertainty_spec(target, distribution = c("uniform", "normal", "lognormal", "triangular", "beta", "discrete", "fixed"), parameters = list(), id = NULL, label = NULL, enabled = TRUE)
validate_uncertainty_spec(spec, scenario = NULL)
sample_uncertainty(scenario, n = 1000L, method = c("monte_carlo", "latin_hypercube"), seed = 42L, uncertainty = NULL)
run_uncertainty(scenario, n = 1000L, sampling = c("monte_carlo", "latin_hypercube"), seed = 42L, metrics = NULL, thresholds = list(), method = NULL, continue_on_error = TRUE)
uncertainty_summary(x)
uncertainty_probabilities(x)
global_sensitivity(x, method = c("spearman", "pearson"))
local_sensitivity(scenario, targets = NULL, change = 0.01, metrics = NULL, method = NULL)
plot_uncertainty(x, metric = NULL, type = c("distribution", "interval"))
plot_tornado(x, metric = NULL, method = c("spearman", "pearson"))
stress_shock(target, value, mode = c("set", "add", "multiply"))
stress_case(id, title, shocks, description = "")
run_stress_tests(scenario, cases, metrics = NULL, method = NULL)
stress_test_summary(x)
plot_stress_test(x, metric = NULL, type = c("delta", "terminal"))
}
\value{The constructor and analysis functions return uncertainty specifications, sampled data frames, \code{catalyst_uncertainty_run} objects, sensitivity tables, stress-case records, or \code{catalyst_stress_test} objects. Plot functions return ggplot objects.}
