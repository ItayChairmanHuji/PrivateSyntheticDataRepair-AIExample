---
name: icm-research-analyst
description: Specialized guidance for analyzing experimental results, generating visualizations, and deriving scientific insights. Use when working in Stage 06 or evaluating repair performance.
---

# ICM Research Analyst

This skill helps you turn raw CSV data into scientific plots and interpretable results.

## Analytical Standards
- **Baseline Comparison**: Always compare repaired synthetic data against the initial (noisy) synthetic data.
- **Statistical Rigor**: Use multiple seeds to calculate variance and confidence intervals for metrics.
- **Visual Clarity**:
    - Use `seaborn` or `matplotlib` for plotting.
    - Standardize plot styles (fonts, colors, labels) for publication readiness.

## Common Metrics
- **TVD (Total Variation Distance)**: Measures statistical similarity between distributions.
- **Violation Count**: Counts how many denial constraints are broken.
- **Utility Errors**: Measures performance drop on downstream ML tasks (e.g., Logistic Regression accuracy).

## Workflow (Stage 06)
1.  Load the `aggregated_results.csv` from Stage 07.
2.  Clean and pivot data for plotting.
3.  Generate "Main Effects" plots (e.g., Alpha vs. TVD).
4.  Summarize findings in a Markdown report.
