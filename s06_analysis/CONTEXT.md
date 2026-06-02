# Stage 06: Analysis

## Purpose
Automate the synthesis of research results into interpretable Jupyter Notebooks. This stage transforms aggregated experiment data (from Stage 05 evaluating or remote outputs) into an AI-friendly analysis environment.

## AI-Friendly Workflow
To simplify modifications, the AI should **never edit `.ipynb` JSON files directly**. Instead, use the helper scripts provided in this stage:

### 1. Aggregate Raw Results
First, use the aggregator to combine all evaluation `.json` files from `s05_evaluating/output` (or `remote/output`) into a single flattened CSV file.

```bash
python s06_analysis/src/io/aggregator.py --source s05_evaluating/output --output s06_analysis/input/aggregated_results.csv
```

### 2. Clean & Flatten (Optional)
If you need additional flattening logic, you can load the data through the `ResultFlattener` component (located in `src/io/result_flattener.py`). Alternatively, you can point the notebook directly at the aggregated CSV.

### 3. Generate Notebook from Python Template
Edit or create a standard Python script with `# %%` markers to define your notebook cells. Use `# [MARKDOWN]` below the marker for text cells.
*A comprehensive default template is provided at `s06_analysis/src/analysis/analysis_template.py`.*

Generate the final `.ipynb` file using:
```bash
python s06_analysis/src/io/notebook_generator.py --template s06_analysis/src/analysis/analysis_template.py --output s06_analysis/notebooks/experiment_analysis.ipynb
```

## Contract
**Inputs (Layer 4 - `input/`):**
- Raw JSON files aggregated from `s05_evaluating` or `remote`.
- A `.py` template script acting as the notebook source.

**Outputs (Layer 4 - `output/` & `notebooks/`):**
- `.ipynb`: The generated Jupyter Notebook, ready for the user to open.

## Standard Metrics & Plotting
The default `analysis_template.py` already implements the mandatory research plotting standards:
- **Metrics Evaluated**: Deletion Ratio, Marginals Error, Marginals Loss, TVD, ML Accuracy, and Runtime.
- **Plot Structure**: Datasets are separated into distinct plot columns/subplots.
- **Color (Hue)**: `repair_algorithm`
- **Style (Marker)**: `synthesizer`

## Restricted Execution
Only commands documented in the workflow sections above are allowed. Do NOT apply any manual changes unless explicitly requested.