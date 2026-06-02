# Stage 03: Marginals Obtaining

## Purpose
Extract statistical summaries (marginals) from both private and synthetic data to guide the repair process.

## Usage
To run the stage for a specific dataset using Top-K (default):
```bash
python s03_marginals/src/main.py dataset_name=adult100
```

To load marginals from a pre-existing file:
```bash
python s03_marginals/src/main.py --config-name from_file experiment_name=adult100 path=/path/to/marginals.json
```

To clean the outputs for a specific dataset:
```bash
python s03_marginals/src/io/clean.py --dataset adult100
```

## Restricted Execution
Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes unless explicitly asked.

## Contract
**Inputs (Layer 4 - `input/`)**:
- `s03_marginals/input/<dataset_name>/private_data.csv`: The ground truth private data.
- `s03_marginals/input/<dataset_name>/synthetic_data.csv`: The synthetic data to be evaluated/repaired.
- `s03_marginals/input/<dataset_name>/metadata.json`: Dataset metadata.
- `s03_marginals/input/<dataset_name>/constraints.txt`: Domain constraints (DCs).

**Reference Material (Layer 3 - `config/`)**:
- Marginal selection configurations (e.g., `top_k.yaml`).

**Process**:
1.  Select which attribute sets to calculate marginals for (e.g., using Top-K selection).
2.  Calculate noisy marginals from the private data (Differential Privacy).
3.  Calculate exact marginals from the synthetic data.

**Outputs (Layer 4 - `output/`)**:
- `s03_marginals/output/<dataset_name>/marginals.json`: The set of obtained marginals (noisy private targets vs synthetic values).
