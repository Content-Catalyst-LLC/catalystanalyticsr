\name{export_uncertainty_analysis}
\alias{export_uncertainty_analysis}
\alias{export_stress_test}
\title{Export uncertainty and stress-test bundles}
\description{Writes machine-readable scenario, summary, probability, sensitivity, failure, sample, and manifest files for reproducible review.}
\usage{
export_uncertainty_analysis(x, dir = "catalyst_uncertainty_bundle", prefix = "uncertainty", include_samples = TRUE, zip_bundle = TRUE)
export_stress_test(x, dir = "catalyst_stress_test_bundle", prefix = "stress-test")
}
\value{Invisibly returns generated paths.}
