#!/bin/bash
#SBATCH --job-name=calc_marginals
#SBATCH --output=logs/marginals_%A_%a.out
#SBATCH --error=logs/marginals_%A_%a.err
#SBATCH --time=02:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2

# Create logs directory
mkdir -p logs

# Array index maps to the job
DATASETS=(
adult census compas tax
)

# Get the specific dataset for this array task
DS="${DATASETS[$SLURM_ARRAY_TASK_ID]}"

echo "Running marginals for: dataset=$DS noise_level=1.0"

export PYTHONPATH=$(pwd):$PYTHONPATH

# Activate environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

start_time=$(date +%s)
python -m p_processes.p03_marginals.main dataset_name=$DS noise_level=1.0
exit_code=$?
end_time=$(date +%s)

runtime=$((end_time - start_time))

if [ $exit_code -eq 0 ]; then
    echo "Successfully calculated marginals for $DS. Runtime: $runtime seconds."
else
    echo "Marginals calculation failed for $DS with exit code $exit_code."
fi
