# Ride Sharing Simulation

Full write-up: [rss_report.pdf](./rss_report.pdf)

## Data
- `dat.py` — Computes real-world abandon rate and wait-time KPIs from driver/rider datasets for comparison against simulation output.
- `eval.py` — Plots histograms of simulated KPI distributions with overlaid mean, confidence interval, prediction interval, and observed-value markers.
- `surgepricingfinal.py` — Core discrete-event simulation engine implementing driver/rider arrivals, matching, trip completion, abandonment, and dynamic surge pricing.
- `runsurgepricingfinal.py` — Runs the surge-pricing simulation across multiple replications and reports KPI means, confidence intervals, and prediction intervals.
