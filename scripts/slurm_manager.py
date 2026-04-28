import subprocess
import argparse
import os
import yaml
import datetime
import zipfile
from pathlib import Path

def get_config():
    config_path = Path("config/remote/slurm.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run_remote(host, cmd):
    return subprocess.run(["ssh", host, cmd], capture_output=True, text=True)

def push(cfg):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    print(f"Pushing code to {host}:{remote_dir}...")
    
    run_remote(host, f"mkdir -p {remote_dir}")
    
    # Get tracked files
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    files = result.stdout.splitlines()
    if os.path.exists("license.json"):
        files.append("license.json")
        
    zip_name = "codebase.zip"
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file)
            else:
                # Handle directories tracked by git
                if os.path.isdir(file):
                    for root, dirs, fnames in os.walk(file):
                        for fname in fnames:
                            zipf.write(os.path.join(root, fname))
                
    subprocess.run(["scp", zip_name, f"{host}:{remote_dir}/"])
    run_remote(host, f"cd {remote_dir} && unzip -o {zip_name} && rm {zip_name}")
    os.remove(zip_name)
    print("Push complete.")

def submit(cfg, experiments):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    # Ensure logs directory exists on remote
    run_remote(host, f"mkdir -p {remote_dir}/logs")
    
    for i, exp_overrides in enumerate(experiments):
        # Generate a unique name for the job
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        job_name = f"exp_{timestamp}_{i}"
        
        slurm_cfg = cfg['slurm_defaults']
        script_content = [
            "#!/bin/bash",
            f"#SBATCH --job-name={job_name}",
            f"#SBATCH --partition={slurm_cfg['partition']}",
            f"#SBATCH --time={slurm_cfg['time']}",
            f"#SBATCH --nodes={slurm_cfg['nodes']}",
            f"#SBATCH --ntasks={slurm_cfg['ntasks']}",
            f"#SBATCH --cpus-per-task={slurm_cfg['cpus_per_task']}",
            f"#SBATCH --mem={slurm_cfg['mem']}",
            f"#SBATCH --output=logs/%x_%j.out",
            f"#SBATCH --error=logs/%x_%j.err",
            "",
            f"cd {remote_dir}",
            "mkdir -p logs results outputs",
            f"export PYTHONPATH=$PYTHONPATH:{remote_dir}",
            f"{cfg['python_env']} main.py {exp_overrides}"
        ]
        
        script_name = f"submit_{job_name}.sh"
        with open(script_name, "w") as f:
            f.write("\n".join(script_content))
            
        subprocess.run(["scp", script_name, f"{host}:{remote_dir}/"])
        res = run_remote(host, f"cd {remote_dir} && sbatch {script_name}")
        print(f"Submitted {exp_overrides}: {res.stdout.strip()}")
        
        # Keep the script on remote but delete locally
        os.remove(script_name)

def status(cfg):
    host = cfg['host']
    print(f"--- Active Jobs for {host} ---")
    res = run_remote(host, "squeue -u $(whoami)")
    if res.stdout:
        print(res.stdout)
    else:
        print("No active jobs found.")
    
    print("--- Recent Job History (sacct) ---")
    res = run_remote(host, "sacct --format=JobID,JobName,State,ExitCode,TimeLimit,Elapsed -n -X | tail -n 10")
    if res.stdout:
        print(res.stdout)
    else:
        print("No history found.")

def pull(cfg):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    print(f"Pulling results and outputs from {host}:{remote_dir}...")
    
    # Sync results
    subprocess.run(["scp", "-r", f"{host}:{remote_dir}/results", "."])
    # Sync outputs
    subprocess.run(["scp", "-r", f"{host}:{remote_dir}/outputs", "."])
    print("Pull complete.")

def logs(cfg):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    print(f"Pulling logs from {host}:{remote_dir}...")
    subprocess.run(["scp", "-r", f"{host}:{remote_dir}/logs", "."])
    print("Logs pulled to local logs/ directory.")

def main():
    parser = argparse.ArgumentParser(description="Slurm Experiment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    subparsers.add_parser("push", help="Push code to remote server")
    
    submit_parser = subparsers.add_parser("submit", help="Submit experiments to Slurm")
    submit_parser.add_argument("experiments", nargs="+", help="Hydra overrides for each experiment")
    
    subparsers.add_parser("status", help="Check job status")
    subparsers.add_parser("pull", help="Pull results from remote server")
    subparsers.add_parser("logs", help="Pull logs from remote server")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    try:
        cfg = get_config()
    except Exception as e:
        print(e)
        return

    if args.command == "push":
        push(cfg)
    elif args.command == "submit":
        submit(cfg, args.experiments)
    elif args.command == "status":
        status(cfg)
    elif args.command == "pull":
        pull(cfg)
    elif args.command == "logs":
        logs(cfg)

if __name__ == "__main__":
    main()
