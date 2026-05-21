---
name: icm-experiment-orchestrator
description: Expert guidance for managing high-volume experiments, Slurm deployment, and result synchronization in the ICM framework. Use when planning sweeps or scaling to the remote cluster.
---

# ICM Experiment Orchestrator

This skill handles the logistics of moving research from local development to large-scale execution on Snorlax (Slurm).

## Key Workflows

### 1. Generating Blueprints (Stage 00)
- **Input**: A sweep template (YAML).
- **Process**: Generate a physical folder for every experiment combination.
- **Goal**: Absolute reproducibility. The blueprint contains the exact config every job will run.

### 2. Slurm Deployment (Stage 06)
- **Checklist**:
    - [ ] `rsync` the current code and `00_shared` to the server.
    - [ ] Perform a **Canary Run** (1 job) to verify the environment.
    - [ ] Submit the job array using `sbatch`.
- **Monitoring**: Track job states (`PD`, `R`, `F`) and map them back to the experiment IDs.

### 3. Result Retrieval (Stage 07)
- **Incremental Sync**: Only download `results.json` files for jobs that have successfully completed.
- **Aggregation**: Combine hundreds of JSON files into a single `aggregated_results.csv` for analysis.

## Safeguards
- **Never hardcode paths**: Use the relative paths defined in the ICM contracts.
- **Protect Credentials**: Use SSH keys for Snorlax access.
