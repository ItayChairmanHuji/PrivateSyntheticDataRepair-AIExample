# Stage 04: Repairing

## Purpose
The core algorithmic stage. Use the obtained marginals to "mend" the synthetic data, reducing its error relative to the private data while maintaining utility.

## Contract
**Inputs (Layer 4 - `input/`):**
- `synthetic_data.csv` from `02_synthesizing/output/`.
- `marginals.pkl` from `03_marginals_obtaining/output/`.

**Reference Material (Layer 3 - `config/`):**
- Repairer configurations (e.g., `weighted_vc.yaml`, `ilp.yaml`).

**Process:**
- Identify violations or high-error regions in the synthetic data.
- Apply the repair algorithm to update rows or delete problematic records.

**Outputs (Layer 4 - `output/`):**
- `repaired_data.csv`: The final, mended synthetic dataset.

## Agent Context Directive (Layer 2)
To maintain token efficiency and follow the ICM methodology:
1. **Scope**: Only read files within `icm_sandbox/04_repairing/` and `icm_sandbox/00_shared/`.
2. **Prioritization**:
   - Read `CONTEXT.md` (this file) first to understand the contract.
   - Read `config/` to understand parameter options.
   - Read `src/main.py` to understand the entry point.
   - Check `input/` for required artifacts. **Do not read large data files in full.**
3. **Isolation**: Do not reference `02_synthesizing` or `03_marginals_obtaining` directly. All data must be in `input/`.
