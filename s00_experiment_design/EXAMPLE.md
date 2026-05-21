# Stage 00 Execution Example: Alpha Sweep

This example demonstrates how to run Stage 00 to generate a "Blueprint" for a parameter sweep over `alpha` (repair strength).

## 1. What you need to insert (Input)
In `s00_experiment_design/config/`, you create a master template:

**File: `config/alpha_sweep_template.yaml`**
```yaml
experiment_group: alpha_sweep_may2026
base_config:
  dataset: adult
  epsilon: 1.0
  synthesizer: aim

sweep_parameters:
  repairing.alpha: [0.0, 0.25, 0.5, 0.75, 1.0]
  seed: [42, 43, 44] # 3 seeds per alpha
```

## 2. What I expect to see (Process)
I expect a generator script in `src/` that reads this template and creates the physical workspace for the sweep.

**Command:**
```powershell
python s00_experiment_design/src/generate_blueprint.py --template alpha_sweep_template.yaml
```

## 3. What I will output (Output)
The script will populate `s00_experiment_design/output/` with a self-contained "Blueprint" folder.

**Folder: `output/alpha_sweep_may2026/`**
```text
├── blueprint_summary.json  # Master mapping of Job ID -> Parameters
├── exp_001/
│   └── config.yaml         # alpha=0.0, seed=42
├── exp_002/
│   └── config.yaml         # alpha=0.0, seed=43
...
└── exp_015/
    └── config.yaml         # alpha=1.0, seed=44
```

### Example `blueprint_summary.json`
```json
{
  "group_name": "alpha_sweep_may2026",
  "total_jobs": 15,
  "jobs": {
    "001": {"alpha": 0.0, "seed": 42},
    "002": {"alpha": 0.0, "seed": 43},
    ...
  }
}
```

## Why this is useful:
Before you ever touch the remote server (Stage 06), you can open `exp_005/config.yaml` and verify that the parameters are exactly what you intended. The folder structure itself becomes the "truth" of the experiment design.
