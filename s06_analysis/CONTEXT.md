# Stage 06: Analysis

## Purpose
Automate the synthesis of research results into interpretable Jupyter Notebooks. This stage transforms aggregated experiment data (pulled from remote or generated locally) into a "Glass Box" analysis environment.

## Usage
To generate an analysis notebook for an experiment:
```bash
python s06_analysis/src/main.py experiment_name=experiment_4
```

To clean generated notebooks:
```bash
python s06_analysis/src/io/clean.py
```

## Contract
**Inputs (Layer 4 - `input/`):**
- Aggregated CSV results (e.g., `experiment_4_summary.csv`). These are typically pulled from the `remote/output/` or consolidated from multiple `s05_evaluating` runs.

**Outputs (Layer 4 - `output/`):**
- `notebooks/<experiment_name>_analysis.ipynb`: A generated notebook with pre-filled analysis cells.
- `plots/`: (Generated when the notebook is run) Publication-quality visualizations.
- `tables/`: (Generated when the notebook is run) Summary tables in Markdown/LaTeX.

## Process
1. **Orchestration**: The `StageOrchestrator` identifies the experiment type and target summary file.
2. **Notebook Generation**: A boilerplate notebook is created using `nbformat`, importing modular analysis functions from `s06_analysis/src/analysis/`.
3. **Glass Box Interaction**: The researcher opens the generated notebook to inspect trends, adjust plot parameters, and document conclusions.

## Restricted Execution
Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes unless explicitly asked.

## Stage Rules
- **No Logic in Notebooks**: All complex data processing and plotting MUST reside in `src/analysis/`.
- **Reproducibility**: The generated notebook MUST be self-contained (i.e., it knows where its input data is located).
- **Consistency**: Use standardized themes (Seaborn whitegrid) and color palettes for all plots.
