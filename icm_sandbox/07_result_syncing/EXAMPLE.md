# Stage 07 Execution Example: Syncing Results

## 1. What you need to insert (Input)
- `job_ids.json` from Stage 06.

## 2. What I expect to see (Process)
The script connects to Snorlax, checks which jobs are finished, and `rsync`s their `results.json` files.

**Command:**
```powershell
python 07_result_syncing/src/sync.py --job_ids output/job_ids.json
```

## 3. What I will output (Output)
- `aggregated_results.csv`: A table where each row is one experiment result.
- `synced_data/`: A local mirror of all successful remote output folders.
