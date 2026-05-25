# Remote Utility

This folder contains utilities for interacting with the remote Slurm cluster. It handles code synchronization, job deployment, and result retrieval.

## Usage

### Push Code
Synchronize the local codebase with the remote server.
**Note:** Large folders like `data/`, `outputs/`, `models/`, and `remote/output/` are EXCLUDED by default to keep synchronization fast.
```bash
# Push everything (excluding large ignores)
python -m remote.src.main mode=push

# Push specific files or folders (bypasses default exclusions if explicitly named)
python -m remote.src.main mode=push "paths=[s01_loading/src, route.py]"
```

### Deploy Experiments
Submit a Slurm Array job for a specific blueprint.
```bash
python -m remote.src.main mode=deploy blueprint=experiment_5_repair_comparison
```
Use `canary=true` to run only the first job as a test.

### Rerun Experiment
Clean remote state and resubmit an experiment. This will:
1. Push latest code/config.
2. Cancel any running jobs for this blueprint.
3. Delete previous remote outputs for this blueprint (handled via background process for large directories).
4. Resubmit the full array.
```bash
python -m remote.src.main mode=rerun blueprint=experiment_5_repair_comparison
```

### Pull Results
Retrieve and aggregate experiment results from the remote server.
**Note:** Raw data folders in `outputs/` are EXCLUDED from the zip by default to prevent timeouts. Only `s05_evaluating` JSON results are pulled unless specified.
```bash
# Pull results for an experiment group (Aggregates evaluation JSONs)
python -m remote.src.main mode=pull blueprint=experiment_1_generation

# Pull ONLY stats (JSONs) for large sweeps (Prevents timeouts)
python -m remote.src.main mode=pull blueprint=experiment_4_repair_comparison stats_only=true

# Pull specific experiments by ID
python -m remote.src.main mode=pull blueprint=experiment_3_repair_comparison "exp_ids=[1, 5, 10]"

# Pull specific files or folders from remote
python -m remote.src.main mode=pull "paths=[outputs/experiment_1_generation/exp_001/s05_evaluating/result_1.json]"
```

### Clean Outputs
Clear the local `remote/output/` folder.
```bash
python remote/src/io/clean.py
```

## Contract

**Inputs:**
- Blueprints in `remote/input/` (usually routed from `mission_control/blueprints/`).
- Remote artifacts on the Slurm cluster.

**Outputs:**
- `remote/output/[blueprint]_summary.csv`: Aggregated results.
- `remote/output/logs/`: Local mirror of remote Slurm logs (if synced).

## Restricted Execution
Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes unless explicitly asked.
