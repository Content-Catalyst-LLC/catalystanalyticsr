# Repository Architecture

Catalyst Analytics R has two layers:

## 1. R package layer

The R package contains deeper reproducible analytics:

- vector dynamics
- RK4 / Euler simulation
- adjusted net savings
- carbon budget checks
- indicator summaries
- plots
- export bundles

## 2. WordPress demo layer

The WordPress plugin provides a lightweight browser demo for public education and lead-in explanation. It does not run the R package server-side.

## Why separate them?

This separation keeps the public site fast and low-risk while preserving the R package for serious reproducible work.
