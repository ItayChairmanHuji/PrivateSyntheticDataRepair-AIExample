# Stage 06: Analysis

## Purpose
The final destination of the research lifecycle. Synthesize results from all experiments into interpretable insights, plots, and tables.

## Contract
**Inputs (Layer 4 - `input/`):**
- Aggregated CSV/JSON results from `07_result_syncing/output/`.
- Individual experiment artifacts (if deep-diving into specific failures).

**Process:**
- Use Jupyter Notebooks in `tests/` or `notebooks/` for interactive exploration.
- Use `src/` for reusable plotting functions and statistical tests.

**Outputs (Layer 4 - `output/`):**
- Publication-quality plots (PNG/PDF).
- Summary tables (Markdown/LaTeX).
- Final project report/conclusion.

## Stage Rules
- Notebooks should be organized by experiment group (e.g., `alpha_sweep_analysis.ipynb`).
- Keep the notebooks clean: move complex data processing logic into `src/`.
