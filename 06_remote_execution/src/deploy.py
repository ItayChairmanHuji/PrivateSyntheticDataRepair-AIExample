import subprocess
import argparse
import yaml
import json
import os
from pathlib import Path

def get_slurm_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def deploy_blueprint(blueprint_path, config_path):
    cfg = get_slurm_config(config_path)
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    blueprint_path = Path(blueprint_path)
    group_name = blueprint_path.name
    
    print(f"Deploying blueprint '{group_name}' to {host}...")
    
    # 1. Push Code and Blueprint
    # For the sandbox example, we'll use a simplified rsync
    exclude = [".git/", ".venv/", "__pycache__/", "results/", "outputs/", "logs/"]
    exclude_args = [f"--exclude={e}" for e in exclude]
    
    # Push local sandbox to remote
    subprocess.run(["rsync", "-avz"] + exclude_args + ["icm_sandbox/", f"{host}:{remote_dir}/icm_sandbox/"])
    
    # 2. Submit Job Array
    # In ICM, we submit the blueprint.json which contains all the info
    print(f"Submitting job array for {group_name}...")
    
    # This would typically trigger a remote sbatch call
    # For now, we simulate the command that would be run on remote
    remote_cmd = f"cd {remote_dir} && sbatch icm_sandbox/06_remote_execution/src/slurm_array_template.sh {group_name}"
    print(f"Remote command: {remote_cmd}")
    # res = subprocess.run(["ssh", host, remote_cmd], capture_output=True, text=True)
    
    # Store dummy job mapping for the example
    job_ids = {"group": group_name, "status": "submitted", "jobs": {}}
    with open("icm_sandbox/06_remote_execution/output/job_ids.json", "w") as f:
        json.dump(job_ids, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", type=str, required=True)
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()
    deploy_blueprint(args.blueprint, args.config)
