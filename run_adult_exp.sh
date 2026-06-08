#!/bin/bash
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

export PYTHONPATH=$(pwd):$PYTHONPATH

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
python3 -m p_processes.p02_synthesizing.p02b_sampling.main \
    dataset_name=adult \
    engine_name=$ENGINE \
    epsilon=$EPS \
    seed=$SEED \
    size=$SIZE \
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

python3 -m p_processes.p04_repairing.$REPAIR_PROC.main \
    dataset_name=adult \
    synthesizer_name=$ENGINE \
    epsilon=$EPS \
    seed=$SEED \
    size=$SIZE \
    noise_level=$MARGINAL_TAG \
    alpha=0.5

# 3. Evaluating
echo "--- Stage 3: Evaluating ---"
python3 -m p_processes.p05_evaluating.main \
    dataset_name=adult \
    synthesizer_name=$ENGINE \
    repairer_name=$REPAIRER \
    epsilon=$EPS \
    seed=$SEED \
    size=$SIZE \
    alpha=0.5 \
    noise_level=$MARGINAL_TAG \
    experiment_id="basic_exp_adult" \
    timestamp="v1"

echo "Job $ID completed."
