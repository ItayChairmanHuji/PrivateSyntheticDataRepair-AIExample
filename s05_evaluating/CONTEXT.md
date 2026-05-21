# Stage 05: Evaluating

## Purpose
Quantify the quality of the repair by comparing the repaired synthetic data to the original private data across various metrics.

## Contract
**Inputs (Layer 4 - `input/`):**
- `private_data.csv`
- `repaired_data.csv`
- `synthetic_data.csv` (baseline)

**Reference Material (Layer 3 - `config/`):**
- Evaluator configurations.

**Process:**
- Compute statistical distance metrics (e.g., Total Variation Distance).
- Compute utility metrics (e.g., downstream ML task performance).
- Compute constraint violation counts.

**Outputs (Layer 4 - `output/`):**
- `results.json`: A structured report of all metrics.

## Stage Rules
- Always compare against the un-repaired synthetic data as a baseline.
