# Stage 07: Result Syncing

## Purpose
Safely retrieve experiment artifacts from the remote server and consolidate them into a format ready for analysis.

## Workflow
1. **Monitor**: Check Slurm queue to ensure jobs are finished.
   ```bash
   ssh snorlax-login "squeue --me"
   ```
2. **Sync**: Pull results for a specific experiment group (e.g., `experiment_1_generation`).
   ```bash
   python s07_sync/src/sync.py --blueprint experiment_1_generation
   ```

## Contract
**Inputs (Layer 4 - `input/`):**
- Remote `outputs/` directory on Snorlax.

**Process:**
- `src/sync.py`: 
    - Uses `rsync` to pull files from `~/final_research/outputs/[blueprint_name]` to the local `outputs/[blueprint_name]`.
    - Automatically walks through all `exp_XXX` subfolders.
    - Aggregates all `result_*.json` files into a single CSV.

**Outputs (Layer 4 - `output/`):**
- `output/[blueprint_name]_summary.csv`: The aggregated metrics for the entire sweep.
- `outputs/[blueprint_name]/`: Local mirror of key artifacts (metadata, run configs, evaluation results).

## Stage Rules
- **Isolation**: Always specify the `--blueprint` to avoid syncing unrelated data.
- **Incremental**: `rsync` is used to only download new or changed files.
- **Cleanup**: Do not delete remote files automatically; keep them as a backup until the project is archived.
