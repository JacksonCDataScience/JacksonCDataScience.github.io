# Ride Sharing Simulation

Full write-up: [rss_report.pdf](./rss_report.pdf)

## Code
- `dat.py` — Computes real-world abandon rate and wait-time KPIs from driver/rider datasets for comparison against simulation output.
- `eval.py` — Plots histograms of simulated KPI distributions with overlaid mean, confidence interval, prediction interval, and observed-value markers.
- `surgepricingfinal.py` — Core discrete-event simulation engine implementing driver/rider arrivals, matching, trip completion, abandonment, and dynamic surge pricing.
- `runsurgepricingfinal.py` — Runs the surge-pricing simulation across multiple replications and reports KPI means, confidence intervals, and prediction intervals.
- `sim.py` — Baseline discrete-event simulation of the BoxCar system using the original modeling assumptions.
- `rev_sim.py` — Revised simulation engine using data-calibrated parameters passed via a coef dictionary.
- `Simulation FINAL.ipynb` — Runs EDA and the baseline simulation, showing it doesn't match the real data.
- `Revised_Simulation FINAL.ipynb` — Tests the model's assumptions against real data, then reruns the simulation with corrected parameters.
