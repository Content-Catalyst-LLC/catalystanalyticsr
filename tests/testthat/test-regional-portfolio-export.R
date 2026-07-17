test_that("regional portfolio export writes governed artifacts", {
  analysis <- regional_portfolio_analysis(regional_portfolio_fixture(),regional_budget_fixture(),sector_pathway_fixture())
  out <- export_regional_portfolio_analysis(analysis,tempdir(),prefix=paste0("regional-",sample.int(1e8,1)),zip_bundle=FALSE,quiet=TRUE)
  expect_true(file.exists(out$manifest_path)); expect_true(out$manifest$file_count >= 8L)
  expect_true(all(c("member-indicators.csv","portfolio-aggregates.csv","regional-comparison.csv","regional-carbon-diagnostics.csv","sector-transition-summary.csv") %in% basename(out$files)))
})
