import os
import subprocess
from pathlib import Path

datasets = ["adult", "census", "compas", "tax"]
algorithms = ["aim", "mst", "patectgan"]
epsilons = [0.001, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

jobs = []
for ds in datasets:
    for algo in algorithms:
        for eps in epsilons:
            # Check if model exists
            model_path = Path(f"r_resources/r_models/{ds}/{algo}/{eps}/42.pkl")
            if not model_path.exists():
                jobs.append((ds, algo, eps))

print(f"Total jobs to run: {len(jobs)}")

if not jobs:
    print("All models are already trained!")
    exit(0)

# Create a master sbatch script or submit them one by one.
# An array job is best.
bash_script = """#!/bin/bash
#SBATCH --job-name=train_models
#SBATCH --output=logs/train_%A_%a.out
#SBATCH --error=logs/train_%A_%a.err
#SBATCH --time=24:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4

# Create logs directory
mkdir -p logs

# Array index maps to the job
PARAMS=(
{params_list}
)

# Get the specific parameters for this array task
TASK_PARAMS="${PARAMS[$SLURM_ARRAY_TASK_ID]}"
read -r DS ALGO EPS <<< "$TASK_PARAMS"

echo "Running: dataset=$DS engine=$ALGO epsilon=$EPS"

export PYTHONPATH=$(pwd):$PYTHONPATH
python -m p_processes.p02_synthesizing.p02a_training.main dataset_name=$DS engine=$ALGO epsilon=$EPS
"""

params_lines = []
for ds, algo, eps in jobs:
    params_lines.append(f'"{ds} {algo} {eps}"')

bash_script = bash_script.replace("{params_list}", "\n".join(params_lines))

with open("train_all.sh", "w") as f:
    f.write(bash_script)

print("Generated train_all.sh. To submit: sbatch --array=0-{} train_all.sh".format(len(jobs) - 1))
