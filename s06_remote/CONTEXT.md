# Stage 06: Remote Execution

## Purpose
Bridge the local sandbox with the remote Slurm cluster (Snorlax). Handle deployment, job submission, and monitoring of large-scale experiment sweeps.

## Remote Environment
- **Host**: `snorlax-login`
- **Path**: `~/final_research`
- **Venv**: `~/final_research/.venv`
- **Data**: `~/final_research/data` (Managed separately, do not sync)

## Workflow
1. **Prepare Blueprint**: Generate experiments in `s00_experiment_design` and route to `s06_remote/input`.
2. **Synchronize**: Push local code changes to the remote server.
   ```bash
   python s06_remote/src/sync_to_remote.py
   ```
3. **Deploy**: Submit a Slurm Array job to the cluster.
   ```bash
   python s06_remote/src/deploy.py --blueprint experiment_1_generation
   ```

## Contract
**Inputs (Layer 4 - `input/`):**
- Experiment Blueprint from `s00_experiment_design/output/` (routed to `s06_remote/input/`).
- Current project source code.

**Process:**
- `src/sync_to_remote.py`: Zips and uploads code (excluding large/unnecessary folders).
- `src/deploy.py`: Triggers the Slurm submission on the remote host.
- `src/run_experiment.py`: (Remote only) Orchestrates stages 01-05 for a specific job index.
- `src/slurm_array.sh`: (Remote only) The SBATCH script defining job parameters and array range.

**Outputs (Layer 4 - `output/`):**
- `job_ids.json`: Mapping of local experiment IDs to Slurm Job IDs.
- `outputs/[group_name]/exp_XXX/`: The full trace of the experiment, containing subfolders for each stage's output (e.g., `s01_loading/`, `s02_synthesizing/`, etc.).

## Stage Rules
- **Canary First (Mandatory)**: Always run a single experiment (e.g., job 001) using `--canary` before submitting the full array. Verify that the job finishes correctly and produces the expected artifacts.
- **Isolation**: Each Slurm job runs in a unique temporary directory to avoid file collisions between parallel stages.
- **Logging**: All stdout/stderr from Slurm jobs is directed to `~/final_research/s06_remote/output/logs/`.
