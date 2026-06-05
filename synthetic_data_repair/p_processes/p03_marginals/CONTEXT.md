# Process: p03_marginals

## Purpose
Calculates target marginals for a dataset, used for evaluating utility and guiding repair.

## Contract
- **Input Resource**: `r_resources/r_data/private/{dataset_name}/data.csv`
- **Output Resource**: `r_resources/r_marginals/{dataset_name}/{noise}/marginals.json`

## Usage
```bash
python -m p_processes.p03_marginals.main dataset_name=adult100 noise_level=0.0
```
