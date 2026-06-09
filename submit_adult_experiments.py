import os
from pathlib import Path

# Experiment Parameters
dataset = "adult"
engines = ["aim", "mst", "patectgan"]
seeds = list(range(1, 9))
repairers = ["vanilla_vc", "classic_vc", "weighted_vc"]

# Default Values (when not sweeping)
def_epsilon = 0.5
def_size = 500000
def_marginals = 50
def_alpha = 0.5

# Sweep Values
epsilons = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
sizes = [100000, 250000, 500000, 750000, 1000000]
marginal_counts = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

jobs = []

# 1. Epsilon Sweep
for engine in engines:
    for eps in epsilons:
        for seed in seeds:
            for repairer in repairers:
                jobs.append({
                    "type": "epsilon_sweep",
                    "engine": engine,
                    "eps": eps,
                    "seed": seed,
                    "size": def_size,
                    "marginals": def_marginals,
                    "repairer": repairer
                })

# 2. Size Sweep
for engine in engines:
    for size in sizes:
        if size == def_size: continue # Already covered in epsilon sweep (eps=0.5)
        for seed in seeds:
            for repairer in repairers:
                jobs.append({
                    "type": "size_sweep",
                    "engine": engine,
                    "eps": def_epsilon,
                    "seed": seed,
                    "size": size,
                    "marginals": def_marginals,
                    "repairer": repairer
                })

# 3. Marginals Sweep
for engine in engines:
    for m_count in marginal_counts:
        if m_count == def_marginals: continue # Already covered in epsilon sweep (eps=0.5, size=500k)
        for seed in seeds:
            for repairer in repairers:
                jobs.append({
                    "type": "marginals_sweep",
                    "engine": engine,
                    "eps": def_epsilon,
                    "seed": seed,
                    "size": def_size,
                    "marginals": m_count,
                    "repairer": repairer
                })

print(f"Total jobs generated: {len(jobs)}")

# Create the parameter file for Slurm
with open("experiment_params.txt", "w") as f:
    for i, job in enumerate(jobs):
        line = f"{i} {job['type']} {job['engine']} {job['eps']} {job['seed']} {job['size']} {job['marginals']} {job['repairer']}\n"
        f.write(line)

# Create the wrapper script
wrapper_script = """#!/bin/bash
#SBATCH --job-name=adult_exp
#SBATCH --output=logs/exp_%A_%a.out
#SBATCH --error=logs/exp_%A_%a.err
#SBATCH --time=08:00:00
#SBATCH --mem=64G
#SBATCH --cpus-per-task=2

set -euo pipefail

mkdir -p logs

# Get parameters for this task (with OFFSET support)
REAL_ID=$((SLURM_ARRAY_TASK_ID + ${OFFSET:-0}))
PARAM_FILE="experiment_params.txt"
LINE=$(sed -n "$((REAL_ID + 1))p" $PARAM_FILE)
read -r ID TYPE ENGINE EPS SEED SIZE MARGINALS REPAIRER <<< "$LINE"

echo "Running Job $REAL_ID: Type=$TYPE Engine=$ENGINE Eps=$EPS Seed=$SEED Size=$SIZE Marginals=$MARGINALS Repairer=$REPAIRER"

export PYTHONPATH=$(pwd):${PYTHONPATH:-}

# Activate environment
if [ -d ".venv" ]; then
    LOCAL_VENV="/tmp/${USER}/final_research_venv"
    VENV_READY="$LOCAL_VENV/.ready"
    mkdir -p "/tmp/${USER}"
    (
        flock 9
        if [ ! -f "$VENV_READY" ]; then
            rm -rf "$LOCAL_VENV"
            cp -a .venv "$LOCAL_VENV"
            touch "$VENV_READY"
        fi
    ) 9>"/tmp/${USER}/final_research_venv.lock"
    export VIRTUAL_ENV="$LOCAL_VENV"
    export PATH="$LOCAL_VENV/bin:$PATH"
    hash -r
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

# 1. Sampling
echo "--- Stage 1: Sampling ---"
python3 -m p_processes.p02_synthesizing.p02b_sampling.main \\
    dataset_name=adult \\
    engine_name=$ENGINE \\
    epsilon=$EPS \\
    seed=$SEED \\
    size=$SIZE \\
    model_seed=42

# 2. Repairing
echo "--- Stage 2: Repairing ---"
# Map repairer name to process
if [ "$REPAIRER" == "vanilla_vc" ]; then
    REPAIR_PROC="p04a_vanilla_repairing"
elif [ "$REPAIRER" == "classic_vc" ]; then
    REPAIR_PROC="p04b_classic_repairing"
else
    REPAIR_PROC="p04c_weighted_repairing"
fi

# Marginals noise level tag
MARGINAL_TAG="1.0_sampled_$MARGINALS"

python3 -m p_processes.p04_repairing.$REPAIR_PROC.main \\
    dataset_name=adult \\
    synthesizer_name=$ENGINE \\
    epsilon=$EPS \\
    seed=$SEED \\
    size=$SIZE \\
    noise_level=$MARGINAL_TAG \\
    alpha=0.5

# 3. Evaluating
echo "--- Stage 3: Evaluating ---"
python3 -m p_processes.p05_evaluating.main \\
    dataset_name=adult \\
    synthesizer_name=$ENGINE \\
    repairer_name=$REPAIRER \\
    epsilon=$EPS \\
    seed=$SEED \\
    size=$SIZE \\
    alpha=0.5 \\
    noise_level=$MARGINAL_TAG \\
    experiment_id="basic_exp_adult" \\
    timestamp="v2"

echo "Job $ID completed."
"""

with open("run_adult_exp.sh", "w") as f:
    f.write(wrapper_script)

print("Generated run_adult_exp.sh and experiment_params.txt.")
if len(jobs) > 1000:
    print("Large job detected. Submit in parts:")
    for offset in range(0, len(jobs), 1000):
        end = min(offset + 999, len(jobs) - 1)
        count = end - offset + 1
        print(f"sbatch --export=OFFSET={offset} --array=0-{count-1} run_adult_exp.sh")
else:
    print(f"To submit: sbatch --array=0-{len(jobs)-1} run_adult_exp.sh")
