# Remote Utility

This folder contains utilities for interacting with the remote Slurm cluster. It handles code synchronization, job deployment, and result retrieval.

## Usage

### Push Code
Synchronize the local codebase with the remote server.
```bash
# Push everything (excluding ignores)
python remote/src/main.py mode=push

# Push specific files or folders (folders will be zipped)
python remote/src/main.py mode=push "paths=[s01_loading/src, route.py]"
```

### Deploy Experiments
Submit a Slurm Array job for a specific blueprint.
```bash
python remote/src/main.py mode=deploy blueprint=experiment_1_generation
```
Use `canary=true` to run only the first job as a test.

### Pull Results
Retrieve and aggregate experiment results from the remote server.
```bash
# Pull results for an experiment group
python remote/src/main.py mode=pull blueprint=experiment_1_generation

# Pull specific experiments by ID
python remote/src/main.py mode=pull blueprint=experiment_3_repair_comparison "exp_ids=[1, 5, 10]"

# Pull specific files or folders from remote
python remote/src/main.py mode=pull "paths=[outputs/experiment_1_generation/exp_001/s05_evaluating/result_1.json]"
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
