# Stage 05: Evaluating

## Purpose
Quantify the quality of the repair by comparing the repaired synthetic data to the original private data across various metrics.

## Usage
To run the evaluation for a specific dataset:
```bash
python s05_evaluating/src/main.py dataset_name=adult100
```

To clean the output directory:
```bash
# Clean all outputs
python s05_evaluating/src/cli/clean.py

# Clean specific dataset output
python s05_evaluating/src/cli/clean.py --dataset adult100
```

## Restricted Execution
Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes unless explicitly asked.

## Contract
**Inputs (Layer 4 - `input/`):**
All inputs MUST be located in `input/<dataset_name>/`.
- `private_data.csv`: The original sensitive data.
- `synthetic_data.csv`: The un-repaired synthetic data (baseline).
- `repaired_data.csv`: The repaired synthetic data.
- `metadata.json`: Dataset metadata (target column, etc.).
- `constraints.txt`: Domain constraints (DCs).
- `marginals.json`: The marginals used for synthesis/repair.

**Outputs (Layer 4 - `output/`):**
All outputs will be saved in `output/<dataset_name>/`.
- `results.json`: A structured report of all metrics.
- Other evaluator-specific artifacts (e.g., plots, intermediate CSVs).

## Stage Rules
- Always compare against the un-repaired synthetic data as a baseline.
- All evaluators must be registered in the orchestrator configuration.
