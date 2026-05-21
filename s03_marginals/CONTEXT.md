# Stage 03: Marginals Obtaining

## Purpose
Extract statistical summaries (marginals) from both private and synthetic data to guide the repair process.

## Contract
**Inputs (Layer 4 - `input/`):**
- `private_data.csv` (Private)
- `synthetic_data.csv` (Synthetic)
- `metadata.json`

**Reference Material (Layer 3 - `config/`):**
- Marginal selection configurations (e.g., `top_k.yaml`).

**Process:**
- Select which attribute sets to calculate marginals for.
- Calculate noisy marginals from the private data (DP).
- Calculate exact marginals from the synthetic data.

**Outputs (Layer 4 - `output/`):**
- `marginals.pkl` or `marginals.json`: The set of obtained marginals.

## Stage Rules
- Noisy marginals must be generated using an approved DP mechanism (e.g., Gaussian/Laplace).
