#!/bin/bash
#SBATCH --job-name=exp_20260430_204651_9
#SBATCH --partition=main
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

cd ~/final_research
mkdir -p logs results outputs
export PYTHONPATH=$PYTHONPATH:~/final_research
~/final_research/.venv/bin/python main.py loading.name=adult5000 synthesizing.num_of_iterations=30 synthesizing.seed=43 repairing=weighted_vc experiment_name=adult5000_iters_weighted_vc