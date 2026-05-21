# Internal Readme: Remote Utility

## Components
- `pusher.py`: Handles zipping and uploading code via `scp`. Excludes large directories like `data/` and `outputs/`.
- `puller.py`: Retrieves results from the remote server. Uses `zip` on remote and `scp` to pull, then extracts and aggregates JSON results into a CSV summary.
- `deployer.py`: Orchestrates code sync and `sbatch` submission.
- `runner.py`: The script that runs ON THE REMOTE. It sets up an isolated workspace for each Slurm task and executes the specified stages.
- `slurm_array.sh`: The SBATCH template for array jobs.

## Configuration
Managed via Hydra in `remote/config/config.yaml`.
- `remote_host`: SSH alias or IP of the cluster.
- `remote_dir`: Root directory on the remote server.
