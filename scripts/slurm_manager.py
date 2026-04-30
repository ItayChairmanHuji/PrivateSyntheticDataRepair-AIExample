import subprocess
import argparse
import os
import yaml
import datetime
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
    print(f"Pushing code via git to origin and pulling on {host}:{remote_dir}...")
    
    # 1. Push locally to origin
    subprocess.run(["git", "push", "origin"])
    
    # 2. Pull on remote
    # Assuming remote is already a git repo and has origin set up
    res = run_remote(host, f"cd {remote_dir} && git pull origin main")
    print(res.stdout)
    print("Push complete.")

def submit(cfg, experiments, group_size=3):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    # Ensure logs directory exists on remote
    run_remote(host, f"mkdir -p {remote_dir}/logs")
    
    for i in range(0, len(experiments), group_size):
        chunk = experiments[i : i + group_size]
        
        # Generate a unique name for the job
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        job_name = f"exp_{timestamp}_{i}"
        
        slurm_cfg = cfg['slurm_defaults']
        # Convert remote_dir to absolute path if it starts with ~
        abs_remote_dir = remote_dir.replace("~", f"/u4/{host.split('-')[0]}" if "snorlax" in host else "/home/$(whoami)")
        # Actually it's better to just use a fixed path or get it from remote. 
        # But we already know it's /u4/ichairman/final_research
        abs_remote_dir = "/u4/ichairman/final_research"
        
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
            f"cd {abs_remote_dir}",
            "mkdir -p logs results outputs",
            f"export PYTHONPATH=$PYTHONPATH:{abs_remote_dir}",
            "export HYDRA_FULL_ERROR=1",
        ]
        
        for exp_overrides in chunk:
            script_content.append(f"{abs_remote_dir}/.venv/bin/python main.py {exp_overrides}")
        
        script_name = f"submit_{job_name}.sh"
        with open(script_name, "w", newline='\n') as f:
            f.write("\n".join(script_content))
            
        subprocess.run(["scp", script_name, f"{host}:{remote_dir}/"])
        res = run_remote(host, f"cd {remote_dir} && sbatch {script_name}")
        print(f"Submitted job {job_name} with {len(chunk)} experiments: {res.stdout.strip()}")
        
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

def logs(cfg, lines=50):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    print(f"Checking recent logs from {host}:{remote_dir}/logs...")
    
    res = run_remote(host, f"ls -t {remote_dir}/logs/*.out | head -n 1")
    if res.stdout:
        last_log = res.stdout.strip()
        print(f"--- Tail of {last_log} ---")
        res = run_remote(host, f"tail -n {lines} {last_log}")
        print(res.stdout)
        
        # Also check error log
        err_log = last_log.replace(".out", ".err")
        print(f"--- Tail of {err_log} ---")
        res = run_remote(host, f"tail -n {lines} {err_log}")
        print(res.stdout)
    else:
        print("No logs found.")

def main():
    parser = argparse.ArgumentParser(description="Slurm Experiment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    subparsers.add_parser("push", help="Push code to remote server via git")
    
    submit_parser = subparsers.add_parser("submit", help="Submit experiments to Slurm")
    submit_parser.add_argument("experiments", nargs="+", help="Hydra overrides for each experiment")
    submit_parser.add_argument("--group", type=int, default=3, help="Number of experiments per job")
    
    subparsers.add_parser("status", help="Check job status")
    subparsers.add_parser("pull", help="Pull results from remote server")
    
    logs_parser = subparsers.add_parser("logs", help="Check recent logs")
    logs_parser.add_argument("--lines", type=int, default=50, help="Number of lines to tail")
    
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
        submit(cfg, args.experiments, args.group)
    elif args.command == "status":
        status(cfg)
    elif args.command == "pull":
        pull(cfg)
    elif args.command == "logs":
        logs(cfg, args.lines)

if __name__ == "__main__":
    main()
