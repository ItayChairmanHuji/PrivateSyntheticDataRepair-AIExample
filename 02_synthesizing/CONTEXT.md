# Stage 02: Synthesizing

## Purpose
Generate a synthetic version of the private dataset using various differentially private (DP) or non-DP algorithms.

## Contract
**Inputs (Layer 4 - `input/`):**
- `private_data.csv` and `metadata.json` from `01_loading/output/`.

**Reference Material (Layer 3 - `config/`):**
- Synthesizer configurations (e.g., `aim.yaml`, `mst.yaml`, `patectgan.yaml`).

**Process:**
- Train the generative model on the private data.
- Sample the model to create synthetic rows.

**Outputs (Layer 4 - `output/`):**
- `synthetic_data.csv`: The generated synthetic dataset.

## Stage Rules
- Always record the random seed and hyperparameters in a `run_config.json` in the output.
- For DP synthesizers, ensure the epsilon budget is strictly adhered to.
