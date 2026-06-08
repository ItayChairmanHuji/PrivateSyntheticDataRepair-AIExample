import os
import subprocess
from pathlib import Path

datasets = ["adult", "census", "compas", "tax"]
noise_level = 1.0

bash_script = """#!/bin/bash
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
{datasets_list}
)

# Get the specific dataset for this array task
DS="${DATASETS[$SLURM_ARRAY_TASK_ID]}"

echo "Running marginals for: dataset=$DS noise_level={noise_level}"

export PYTHONPATH=$(pwd):$PYTHONPATH

# Activate environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

start_time=$(date +%s)
python -m p_processes.p03_marginals.main dataset_name=$DS noise_level={noise_level}
exit_code=$?
end_time=$(date +%s)

runtime=$((end_time - start_time))

if [ $exit_code -eq 0 ]; then
    echo "Successfully calculated marginals for $DS. Runtime: $runtime seconds."
else
    echo "Marginals calculation failed for $DS with exit code $exit_code."
fi
"""

datasets_list = " ".join(datasets)
bash_script = bash_script.replace("{datasets_list}", datasets_list)
bash_script = bash_script.replace("{noise_level}", str(noise_level))

with open("submit_marginals.sh", "w") as f:
    f.write(bash_script)

print("Generated submit_marginals.sh. To submit: sbatch --array=0-{} submit_marginals.sh".format(len(datasets) - 1))
