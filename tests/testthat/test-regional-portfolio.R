test_that("geography and sector scopes are governed", {
  geo <- geography_scope("USA", "United States", "country", codes=list(iso3="USA"))
  sector <- sector_scope("energy", "Energy", "ISIC", "D")
  expect_true(validate_geography_scope(geo)); expect_true(validate_sector_scope(sector))
  scenario <- scope_scenario(comparison_scenarios()[[1L]], geo, sector, id="usa-energy")
  expect_equal(scenario$scope$geography$id,"USA"); expect_equal(scenario$scope$sectors,"energy")
})

test_that("regional portfolios aggregate weighted indicators", {
  portfolio <- regional_portfolio_fixture(); expect_s3_class(portfolio,"catalyst_regional_portfolio"); expect_true(validate_regional_portfolio(portfolio))
  summary <- portfolio_aggregate(portfolio)
  expect_equal(summary$weighted_value[summary$indicator=="gdp"],108)
  expect_equal(summary$weighted_value[summary$indicator=="emissions"],36.4)
  comparison <- portfolio_compare_regions(portfolio,"gdp"); expect_equal(comparison$member_id[comparison$rank==1L],"north-energy")
})

test_that("weighted indicator summaries respect groups", {
  data <- data.frame(region=c("a","a","b"),value=c(10,20,30),weight=c(1,3,2))
  result <- weighted_indicator_summary(data,"value","weight","region")
  expect_equal(result$weighted_value[result$region=="a"],17.5)
  expect_equal(result$total_weight[result$region=="b"],2)
})

test_that("regional carbon budgets identify overshoot", {
  budgets <- regional_budget_fixture(); expect_s3_class(budgets,"catalyst_regional_carbon_budgets")
  north <- budgets$diagnostics[budgets$diagnostics$geography_id=="NORTH",]
  expect_true(north$overshoot); expect_equal(north$overshoot_time,2027)
  south <- budgets$diagnostics[budgets$diagnostics$geography_id=="SOUTH",]
  expect_false(south$overshoot)
})

test_that("sector pathways diagnose decoupling", {
  pathways <- sector_pathway_fixture(); expect_s3_class(pathways,"catalyst_sector_transition_pathways")
  expect_true(all(pathways$summary$status=="absolute_decoupling"))
  expect_true(all(pathways$summary$intensity_change < 0))
})

test_that("regional portfolio analysis and JSON round trip preserve contracts", {
  portfolio <- regional_portfolio_fixture(); analysis <- regional_portfolio_analysis(portfolio,regional_budget_fixture(),sector_pathway_fixture())
  expect_s3_class(analysis,"catalyst_regional_portfolio_analysis"); expect_equal(regional_portfolio_summary(analysis)$members,2L)
  path <- tempfile(fileext=".json"); regional_portfolio_to_json(portfolio,path); restored <- regional_portfolio_from_json(path)
  expect_s3_class(restored,"catalyst_regional_portfolio"); expect_equal(names(restored$members),names(portfolio$members))
})

test_that("workspaces retain reusable regional portfolios", {
  workspace <- catalyst_workspace("regional-workspace","Regional Workspace")
  workspace <- workspace_add_regional_portfolio(workspace,regional_portfolio_fixture())
  restored <- workspace_get_regional_portfolio(workspace,"transition-portfolio")
  expect_s3_class(restored,"catalyst_regional_portfolio")
  expect_equal(workspace_manifest(workspace)$counts$regional_portfolios,1L)
})

test_that("regional portfolio price year normalizes JSON null and omission", {
  portfolio <- regional_portfolio_fixture()
  portfolio["price_year"] <- list(NA_integer_)
  path <- tempfile(fileext = ".json")
  regional_portfolio_to_json(portfolio, path)
  restored <- regional_portfolio_from_json(path)
  expect_identical(restored$price_year, NA_integer_)
  expect_true(validate_regional_portfolio(restored))

  payload <- jsonlite::fromJSON(path, simplifyVector = FALSE)
  payload$price_year <- NULL
  jsonlite::write_json(payload, path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null")
  restored_missing <- regional_portfolio_from_json(path)
  expect_identical(restored_missing$price_year, NA_integer_)
  expect_true("price_year" %in% names(restored_missing))
})

test_that("regional portfolio price year validation is nullable and scalar", {
  expect_identical(regional_portfolio("nullable-year", "Nullable year", regional_portfolio_fixture()$members, price_year = NULL)$price_year, NA_integer_)
  expect_error(regional_portfolio("bad-year", "Bad year", regional_portfolio_fixture()$members, price_year = c(2024, 2025)), "single number or NULL")
  expect_error(regional_portfolio("old-year", "Old year", regional_portfolio_fixture()$members, price_year = 1700), "between 1800 and 3000")
})

