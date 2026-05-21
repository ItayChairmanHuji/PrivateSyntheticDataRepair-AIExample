#!/bin/bash
#SBATCH --job-name=icm_sweep
#SBATCH --output=s06_remote/output/logs/job_%a.out
#SBATCH --error=s06_remote/output/logs/job_%a.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=02:00:00

# Load environment
source .venv/bin/activate

# Get job index padded with zeros (e.g., 001, 002...)
JOB_ID=$(printf "%03d" $SLURM_ARRAY_TASK_ID)
BLUEPRINT_NAME=$1
BLUEPRINT_PATH="s06_remote/input/$BLUEPRINT_NAME/blueprint.json"

echo "----------------------------------------------------------------"
echo "Job ID: $JOB_ID"
echo "Blueprint: $BLUEPRINT_NAME"
echo "Host: $(hostname)"
echo "Start Time: $(date)"
echo "----------------------------------------------------------------"

python s06_remote/src/run_experiment.py --job_id $JOB_ID --blueprint_path $BLUEPRINT_PATH

echo "----------------------------------------------------------------"
echo "End Time: $(date)"
echo "----------------------------------------------------------------"
