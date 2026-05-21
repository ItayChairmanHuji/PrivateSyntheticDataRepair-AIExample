# Remote Utility

This folder contains utilities for interacting with the remote Slurm cluster. It handles code synchronization, job deployment, and result retrieval.

## Usage

### Push Code
Synchronize the local codebase with the remote server.
```bash
python remote/src/cli/push.py
```

### Deploy Experiments
Submit a Slurm Array job for a specific blueprint.
```bash
python remote/src/cli/deploy.py --blueprint experiment_1_generation
```
Use `--canary` to run only the first job as a test.

### Pull Results
Retrieve and aggregate experiment results from the remote server.
```bash
python remote/src/cli/pull.py --blueprint experiment_1_generation
```

### Clean Outputs
Clear the local `remote/output/` folder.
```bash
python remote/src/cli/clean.py
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
