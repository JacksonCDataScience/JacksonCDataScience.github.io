# Malicious Insider Email Detection

Full write-up: [med_report.pdf](./med_report.pdf)

## Code
- [`med_code.ipynb`](./Code/med_code.ipynb) — preprocesses CERT insider-threat dataset, constructs sentence-embedding semantic deviation features against rolling/expanding/global clean baselines, fits four candidate anomaly-detection models (z-score, PCA reconstruction, isolation forest, weighted ensemble) across the same three baselines used to calculate semantic deviation, and runs comparative diagnostics (precision-recall curves, permutation importance, bootstrap recall) alongside a visualization of the ensemble score's separation between malicious and non-malicious emails.

