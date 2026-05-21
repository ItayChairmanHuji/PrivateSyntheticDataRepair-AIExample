import subprocess
import argparse
import json
import os
from pathlib import Path

# Configuration
REMOTE_HOST = "snorlax-login"
REMOTE_DIR = "~/final_research"

def run_remote_command(cmd):
    print(f"Executing on {REMOTE_HOST}: {cmd}")
    subprocess.run(["ssh", REMOTE_HOST, f"cd {REMOTE_DIR} && {cmd}"], check=True)

def deploy(blueprint_name, canary_only=False):
    # 1. Sync Code
    print("--- Step 1: Synchronizing Code ---")
    sync_script = Path(__file__).parent / "sync_to_remote.py"
    subprocess.run(["python", str(sync_script)], check=True)
    
    # 2. Prepare Remote Folders
    print("--- Step 2: Preparing Remote Environment ---")
    run_remote_command("mkdir -p s06_remote/output/logs")
    
    # 3. Read Blueprint to get total jobs
    blueprint_local_path = Path(__file__).parent.parent / "input" / blueprint_name / "blueprint.json"
    if not blueprint_local_path.exists():
        print(f"Error: Blueprint {blueprint_name} not found in s06_remote/input/")
        return
    
    with open(blueprint_local_path, "r") as f:
        blueprint = json.load(f)
    
    total_jobs = blueprint["total_jobs"]
    print(f"Blueprint '{blueprint_name}' has {total_jobs} jobs.")
    
    # 4. Submit Slurm Job
    print("--- Step 3: Submitting Slurm Job ---")
    if canary_only:
        array_range = "1"
        print("Running CANARY job only (index 1).")
    else:
        array_range = f"1-{total_jobs}"
        print(f"Submitting full array: {array_range}")
    
    sbatch_cmd = f"sbatch --array={array_range} s06_remote/src/slurm_array.sh {blueprint_name}"
    run_remote_command(sbatch_cmd)
    
    print("--- Deployment Successful ---")
    print(f"Monitor jobs with: ssh {REMOTE_HOST} 'squeue -u $USER'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", type=str, required=True, help="Blueprint name in input/")
    parser.add_argument("--canary", action="store_true", help="Submit only the first job as a canary check")
    args = parser.parse_args()
    
    deploy(args.blueprint, args.canary)
