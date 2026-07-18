# Bayesian Climate Analysis

Full write-up: [bca_report.pdf](./bca_report.pdf)

## Code
- `bca_code.Rmd` — preprocesses CRU temperature and elevation raster data into a spatial panel dataset, constructs a rook-adjacency neighbourhood graph, fits four candidate INLA models (M0–M3) of increasing spatial/temporal complexity, and runs posterior predictive diagnostics (Q-Q plots, Bayesian p-values, CRPS) alongside a mapped visualization of the fitted spatial effect.
