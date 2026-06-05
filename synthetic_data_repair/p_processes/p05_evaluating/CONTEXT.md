# Process: p05_evaluating

## Purpose
Evaluates the utility (marginal error) and privacy of synthetic or repaired data.

## Contract
- **Input Resource**: `r_resources/r_data/{type}/.../data.csv`
- **Output Resource**: `r_resources/r_results/{experiment_id}/{job_id}/eval.json`

## Usage
```bash
python -m p_processes.p05_evaluating.main dataset_name=adult100
```
