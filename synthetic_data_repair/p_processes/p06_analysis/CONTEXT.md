# Process: p06_analysis

## Purpose
Aggregates and visualizes results from experiment sweeps.

## Contract
- **Input Resource**: `r_resources/r_results/{experiment_id}/`
- **Output Resource**: `r_resources/r_analysis/{experiment_id}/plots/`
- **Output Resource**: `r_resources/r_analysis/{experiment_id}/summary.csv`

## Usage
```bash
python -m p_processes.p06_analysis.main experiment_id=E001
```
