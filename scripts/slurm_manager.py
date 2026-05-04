import subprocess
import argparse
import os
import yaml
import datetime
import tempfile
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
    
    # Get current branch
    branch_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    branch = branch_res.stdout.strip()
    if not branch:
        branch = "main"

    print(f"Pushing code via git to origin and pulling on {host}:{remote_dir} (branch: {branch})...")
    
    # 1. Push locally to origin
    subprocess.run(["git", "push", "origin", branch])
    
    # 2. Pull on remote
    res = run_remote(host, f"cd {remote_dir} && git pull origin {branch}")
    print(res.stdout)
    if res.stderr:
        print(f"Errors/Warnings:\n{res.stderr}")
    
    # 3. Pip install requirements
    print("Updating requirements on remote...")
    run_remote(host, f"cd {remote_dir} && ./.venv/bin/pip install -r requirements.txt")
    print("Push complete.")

def submit(cfg, experiments, group_name=None, experiments_per_job=None, script="main.py"):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    slurm_cfg = cfg['slurm_defaults']
    if experiments_per_job is None:
        experiments_per_job = slurm_cfg.get('cpus_per_task', 8)
    
    if group_name is None:
        group_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Ensure directories exist on remote
    run_remote(host, f"mkdir -p {remote_dir}/logs/{group_name} {remote_dir}/results {remote_dir}/outputs")
    
    for i in range(0, len(experiments), experiments_per_job):
        chunk = experiments[i : i + experiments_per_job]
        job_name = f"{group_name}_{i//experiments_per_job}"
        
        # Write overrides to a local temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, newline='\n') as tmp:
            for exp in chunk:
                # Add experiment_name if not present or append to it
                if "experiment_name=" not in exp:
                    exp += f" experiment_name={group_name}"
                tmp.write(exp + "\n")
            tmp_path = tmp.name
        
        remote_overrides_path = f"{remote_dir}/logs/{group_name}/{job_name}_overrides.txt"
        
        # Copy overrides file to remote
        subprocess.run(["scp", tmp_path, f"{host}:{remote_overrides_path}"])
        os.remove(tmp_path)
        
        script_content = [
            "#!/bin/bash",
            f"#SBATCH --job-name={job_name}",
            f"#SBATCH --partition={slurm_cfg['partition']}",
            f"#SBATCH --time={slurm_cfg['time']}",
            f"#SBATCH --nodes={slurm_cfg['nodes']}",
            f"#SBATCH --ntasks={slurm_cfg['ntasks']}",
            f"#SBATCH --cpus-per-task={slurm_cfg['cpus_per_task']}",
            f"#SBATCH --mem={slurm_cfg['mem']}",
            f"#SBATCH --output=logs/{group_name}/%x_%j.out",
            f"#SBATCH --error=logs/{group_name}/%x_%j.err",
            "",
            f"cd {remote_dir}",
            f"export PYTHONPATH=$PYTHONPATH:. ",
            "export HYDRA_FULL_ERROR=1",
            "",
            f"# Run experiments in parallel using the dedicated script",
            f"./.venv/bin/python scripts/run_parallel_experiments.py --script {script} --workers {slurm_cfg['cpus_per_task']} --overrides_file {remote_overrides_path}"
        ]
        
        script_name = f"submit_{job_name}.sh"
        with open(script_name, "w", newline='\n') as f:
            f.write("\n".join(script_content))
            
        subprocess.run(["scp", script_name, f"{host}:{remote_dir}/"])
        res = run_remote(host, f"cd {remote_dir} && sbatch {script_name} && rm {script_name}")
        print(f"Submitted job {job_name} with {len(chunk)} experiments: {res.stdout.strip()}")
        
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
    res = run_remote(host, "sacct --format=JobID,JobName,State,ExitCode,TimeLimit,Elapsed -n -X | tail -n 20")
    if res.stdout:
        print(res.stdout)
    else:
        print("No history found.")

def pull(cfg, group_name=None):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    if group_name:
        print(f"Pulling results for group '{group_name}' from {host}...")
        
        os.makedirs("results", exist_ok=True)
        os.makedirs("outputs", exist_ok=True)
        
        # Use rsync if available, otherwise scp -r
        res = subprocess.run(["rsync", "-avz", f"{host}:{remote_dir}/results/", "results/"])
        if res.returncode != 0:
            print("rsync failed or not available, falling back to scp...")
            subprocess.run(["scp", "-r", f"{host}:{remote_dir}/results/*", "results/"])
            
        subprocess.run(["rsync", "-avz", f"{host}:{remote_dir}/outputs/", "outputs/"])
        
        # Also pull logs for this group
        os.makedirs(f"logs/{group_name}", exist_ok=True)
        subprocess.run(["rsync", "-avz", f"{host}:{remote_dir}/logs/{group_name}/", f"logs/{group_name}/"])
    else:
        print("Pulling all results and outputs from remote...")
        subprocess.run(["rsync", "-avz", f"{host}:{remote_dir}/results/", "results/"])
        subprocess.run(["rsync", "-avz", f"{host}:{remote_dir}/outputs/", "outputs/"])
        subprocess.run(["rsync", "-avz", f"{host}:{remote_dir}/logs/", "logs/"])
    
    print("Pull complete.")

def clean(cfg):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    confirm = input(f"Are you sure you want to clean results and logs on {host}:{remote_dir}? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
        
    print(f"Cleaning results, outputs and logs on {host}...")
    run_remote(host, f"cd {remote_dir} && rm -rf results/* outputs/* logs/*")
    print("Remote clean complete.")

def logs(cfg, group_name=None, lines=50, job_id=None):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    log_dir = f"{remote_dir}/logs"
    if group_name:
        log_dir += f"/{group_name}"
    
    if job_id:
        out_pattern = f"{log_dir}/*_{job_id}.out"
        err_pattern = f"{log_dir}/*_{job_id}.err"
    else:
        # Find the latest .out file in the log_dir
        find_cmd = f"ls -t {log_dir}/*.out | head -n 1"
        res = run_remote(host, find_cmd)
        out_pattern = res.stdout.strip()
        if not out_pattern:
            print(f"No logs found in {log_dir}")
            return
        err_pattern = out_pattern.replace(".out", ".err")

    print(f"Checking logs from {host}: {out_pattern}")
    
    res = run_remote(host, f"tail -n {lines} {out_pattern}")
    print(f"--- Tail of Output Log ({os.path.basename(out_pattern)}) ---")
    print(res.stdout)
    
    res = run_remote(host, f"tail -n {lines} {err_pattern}")
    print(f"--- Tail of Error Log ({os.path.basename(err_pattern)}) ---")
    print(res.stdout)

def main():
    parser = argparse.ArgumentParser(description="Slurm Experiment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    subparsers.add_parser("push", help="Push code to remote server via git and update requirements")
    
    submit_parser = subparsers.add_parser("submit", help="Submit experiments to Slurm")
    submit_parser.add_argument("experiments", nargs="*", help="Hydra overrides for each experiment")
    submit_parser.add_argument("--file", type=str, help="File containing experiments (one per line)")
    submit_parser.add_argument("--name", type=str, help="Name for the experiment group")
    submit_parser.add_argument("--group", type=int, help="Number of experiments per job (defaults to cpus_per_task)")
    submit_parser.add_argument("--script", type=str, default="main.py", help="Script to run (default: main.py)")
    
    subparsers.add_parser("status", help="Check job status")
    
    pull_parser = subparsers.add_parser("pull", help="Pull results from remote server via rsync/scp")
    pull_parser.add_argument("--name", type=str, help="Specific experiment group name to pull")
    
    subparsers.add_parser("clean", help="Clean results and logs on remote server")
    
    logs_parser = subparsers.add_parser("logs", help="Check recent logs")
    logs_parser.add_argument("--name", type=str, help="Experiment group name")
    logs_parser.add_argument("--lines", type=int, default=50, help="Number of lines to tail")
    logs_parser.add_argument("--job_id", type=str, help="Specific Job ID to check")
    
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
        exps = args.experiments
        if args.file:
            with open(args.file, "r") as f:
                exps.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])
        if not exps:
            print("No experiments provided.")
            return
        submit(cfg, exps, args.name, args.group, args.script)
    elif args.command == "status":
        status(cfg)
    elif args.command == "pull":
        pull(cfg, args.name)
    elif args.command == "clean":
        clean(cfg)
    elif args.command == "logs":
        logs(cfg, args.name, args.lines, args.job_id)

if __name__ == "__main__":
    main()
