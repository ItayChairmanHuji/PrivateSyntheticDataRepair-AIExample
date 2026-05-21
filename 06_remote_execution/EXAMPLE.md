# Stage 06 Execution Example: Deploying to Snorlax

## 1. What you need to insert (Input)
- A Blueprint folder from `00_experiment_design/output/`.

**File: `config/snorlax_slurm.yaml`**
```yaml
host: snorlax-login
partition: cpu
max_parallel_jobs: 50
```

## 2. What I expect to see (Process)
The deployer syncs the code and the blueprint to Snorlax and triggers `sbatch`.

**Command:**
```powershell
python 06_remote_execution/src/deploy.py --blueprint output/alpha_sweep --config snorlax_slurm.yaml
```

## 3. What I will output (Output)
- `job_ids.json`: Mapping of your experiment indices to Slurm Job IDs.
- `status/`: Real-time state of the remote queue.
