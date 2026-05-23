# Stage 04: Repairing

## Usage
To run the repairing stage for a specific experiment using a specific repairer:
```bash
python s04_repairing/src/main.py experiment_name=adult100 --config-name vanilla_vc
```

To clean the output directory:
```bash
python s04_repairing/src/io/clean.py --experiment adult100
```

## Restricted Execution
Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes unless explicitly asked.

## Contract

### Inputs (Layer 4 - `input/`)
The following artifacts MUST be present in `s04_repairing/input/<experiment_name>/`:
- `synthetic_data.csv`: The synthetic dataset to be repaired.
- `metadata.json`: Dataset metadata (name, target, etc.).
- `constraints.txt`: Denial constraints to be enforced.
- `marginals.json`: Target marginals to preserve.

### Outputs (Layer 4 - `output/`)
The following artifacts will be produced in `s04_repairing/output/<experiment_name>/`:
- `repaired_data.csv`: The repaired synthetic dataset.
