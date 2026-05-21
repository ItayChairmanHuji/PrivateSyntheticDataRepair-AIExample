# Stage 06: Remote Execution

## Purpose
Bridge the local sandbox with the remote Slurm cluster (Snorlax). Handle deployment, job submission, and monitoring.

## Contract
**Inputs (Layer 4 - `input/`):**
- Experiment Blueprint from `s00_experiment_design/output/`.
- Current project source code (via Git or `rsync`).

**Process:**
- `src/` contains logic to `ssh` into Snorlax.
- Uploads necessary files.
- Executes `sbatch`.
- Polls `squeue` to update job status.

**Outputs (Layer 4 - `output/`):**
- `job_ids.json`: Mapping of local experiment IDs to Slurm Job IDs.
- `remote_logs/`: Streamed stdout/stderr from the remote server.

## Stage Rules
- Never hardcode credentials; use environment variables or SSH keys.
- Always perform a "Canary Check" (single job) before submitting a full array.
