#!/bin/bash
#SBATCH --job-name=exp_20260502_105411_352
#SBATCH --partition=ALL
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

cd ~/final_research
mkdir -p logs results outputs
export PYTHONPATH=$PYTHONPATH:. 
export HYDRA_FULL_ERROR=1

# Run experiments in parallel using the dedicated script
./.venv/bin/python scripts/run_parallel_experiments.py --workers 8 --overrides_file ~/final_research/logs/exp_20260502_105411_352_overrides.txt