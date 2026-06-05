#!/bin/bash
#SBATCH --job-name=adult_300k_vg
#SBATCH --output=adult_300k_vg_%j.log
#SBATCH --error=adult_300k_vg_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=128G
#SBATCH --time=01:00:00

# Load environment
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# Run the test
python -u scaling_test.py
