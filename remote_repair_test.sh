#!/bin/bash
#SBATCH --job-name=adult_300k_repair
#SBATCH --output=adult_300k_repair_%j.log
#SBATCH --error=adult_300k_repair_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=128G
#SBATCH --time=02:00:00

# Load environment
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# Run the repair test
python -u scaling_repair_test.py
