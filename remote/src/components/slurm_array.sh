#!/bin/bash
#SBATCH --job-name=icm_exp
#SBATCH --output=remote/output/logs/exp_%A_%a.out
#SBATCH --error=remote/output/logs/exp_%A_%a.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00

# Usage: sbatch --array=1-N remote/src/components/slurm_array.sh [blueprint_name]

BLUEPRINT_NAME=$1
JOB_ID=$(printf "%03d" $SLURM_ARRAY_TASK_ID)

echo "Starting Slurm Task ID: $SLURM_ARRAY_TASK_ID (Job ID: $JOB_ID)"
echo "Blueprint: $BLUEPRINT_NAME"

# Activate environment
source .venv/bin/activate

# Set PYTHONPATH to project root
export PYTHONPATH=$PYTHONPATH:.

# Run the experiment orchestrator
# Note: we point to the blueprint in remote/input (it was synced by pusher)
python remote/src/components/runner.py --job_id $JOB_ID --blueprint_path remote/input/$BLUEPRINT_NAME/blueprint.json
