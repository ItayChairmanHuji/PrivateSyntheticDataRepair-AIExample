#!/bin/bash
#SBATCH --job-name=sample_marginals
#SBATCH --output=logs/sample_marginals_%A_%a.out
#SBATCH --error=logs/sample_marginals_%A_%a.err
#SBATCH --time=01:00:00
#SBATCH --mem=4G
#SBATCH --cpus-per-task=1

# Create logs directory
mkdir -p logs

# Array index maps to the job
DATASETS=(
adult census compas tax
)

# Get the specific dataset for this array task
DS="${DATASETS[$SLURM_ARRAY_TASK_ID]}"

echo "Sampling marginals for: dataset=$DS noise_level=1.0 sample_size=100"

export PYTHONPATH=$(pwd):$PYTHONPATH

# Activate environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

start_time=$(date +%s)
python -m p_processes.p03b_marginal_sampling.main dataset_name=$DS noise_level=1.0 sample_size=100
exit_code=$?
end_time=$(date +%s)

runtime=$((end_time - start_time))

if [ $exit_code -eq 0 ]; then
    echo "Successfully sampled marginals for $DS. Runtime: $runtime seconds."
else
    echo "Marginal sampling failed for $DS with exit code $exit_code."
fi
