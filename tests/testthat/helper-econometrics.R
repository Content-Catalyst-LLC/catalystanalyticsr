
econometric_panel_fixture <- function() {
  units <- c("treated-a", "treated-b", "control-a", "control-b")
  times <- 1:6
  data <- expand.grid(unit = units, time = times, KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE)
  data$treated <- as.numeric(grepl("treated", data$unit))
  data$post <- as.numeric(data$time >= 4)
  unit_effect <- c("treated-a"=2,"treated-b"=4,"control-a"=-1,"control-b"=1)
  time_effect <- c(0,1,2,3,4,5)
  data$outcome <- 20 + unit_effect[data$unit] + time_effect[data$time] + 5 * data$treated * data$post
  data$event_time <- data$time - 4
  data
}

econometric_its_fixture <- function() {
  data <- data.frame(time=1:20)
  data$outcome <- 10 + 1.5 * data$time + 4 * (data$time >= 11) + 2 * pmax(0, data$time - 11)
  data
}

econometric_synth_fixture <- function() {
  times <- 1:8
  donor_a <- 10 + times
  donor_b <- 20 + 0.5 * times
  treated <- 0.6 * donor_a + 0.4 * donor_b + ifelse(times >= 6, 5, 0)
  data.frame(unit=rep(c("treated","donor-a","donor-b"),each=8),time=rep(times,3),outcome=c(treated,donor_a,donor_b),stringsAsFactors=FALSE)
}

econometric_assumptions_fixture <- function() list(
  causal_assumption("parallel-trends","Parallel trends","Untreated outcomes would have evolved in parallel.","supported",evidence=list(pretrend="stable")),
  causal_assumption("no-interference","No interference","One unit's treatment does not alter another unit's outcome.","required")
)
