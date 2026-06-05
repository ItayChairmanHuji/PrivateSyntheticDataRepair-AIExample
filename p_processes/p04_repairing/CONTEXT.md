# Process: p04_repairing

## Purpose
Repairs synthetic data to satisfy Denial Constraints while preserving statistical utility.

## Contract
- **Input Resource**: `r_resources/r_data/synthetic/.../data.csv`
- **Input Resource**: `r_resources/r_marginals/.../marginals.json`
- **Output Resource**: `r_resources/r_data/repaired/{repairer}/{synth}/{eps}/{seed}/{size}/{alpha}/data.csv`

## Usage
```bash
python -m p_processes.p04_repairing.main dataset_name=adult100 repairer_name=weighted_vc alpha=0.5
```
