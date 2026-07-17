regional_portfolio_fixture <- function() {
  north <- geography_scope("NORTH", "Northern Region", "region", codes=list(m49="001"))
  south <- geography_scope("SOUTH", "Southern Region", "region", codes=list(m49="002"))
  energy <- sector_scope("energy", "Energy", "ISIC", "D")
  transport <- sector_scope("transport", "Transport", "custom", "TR")
  members <- list(
    portfolio_member("north-energy", "North energy", north, energy, weight=60, indicators=list(gdp=list(value=120,unit="index",direction="higher_better"), emissions=list(value=42,unit="MtCO2e",direction="lower_better"))),
    portfolio_member("south-transport", "South transport", south, transport, weight=40, indicators=list(gdp=list(value=90,unit="index",direction="higher_better"), emissions=list(value=28,unit="MtCO2e",direction="lower_better")))
  )
  regional_portfolio("transition-portfolio", "Regional Transition Portfolio", members, description="Regional and sector transition evidence.")
}

regional_budget_fixture <- function() {
  data <- data.frame(geography_id=rep(c("NORTH","SOUTH"),each=3),year=rep(2025:2027,2),net_emissions=c(20,18,16,12,11,10))
  budgets <- data.frame(geography_id=c("NORTH","SOUTH"),carbon_budget=c(50,40))
  regional_carbon_budgets(data,budgets)
}

sector_pathway_fixture <- function() {
  data <- data.frame(geography_id=rep(c("NORTH","SOUTH"),each=3),sector_id=rep(c("energy","transport"),each=3),year=rep(2025:2027,2),output=c(100,105,110,80,85,90),emissions=c(50,44,38,30,29,27))
  sector_transition_pathways(data,geography_col="geography_id")
}
