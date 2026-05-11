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

def run_remote(cfg, cmd):
    host = cfg['host']
    return subprocess.run(["ssh", host, cmd], capture_output=True, text=True)

def push(cfg, use_git=False):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    if use_git:
        # Get current branch
        branch_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        branch = branch_res.stdout.strip()
        if not branch:
            branch = "main"

        print(f"Pushing code via git to origin and pulling on {host}:{remote_dir} (branch: {branch})...")
        
        # 1. Push locally to origin
        subprocess.run(["git", "push", "origin", branch])
        
        # 2. Pull on remote
        res = run_remote(cfg, f"cd {remote_dir} && git pull origin {branch}")
        print(res.stdout)
        if res.stderr:
            print(f"Errors/Warnings:\n{res.stderr}")
    else:
        print(f"Pushing updates to {host}:{remote_dir} via rsync/scp...")
        exclude = [
            ".git/", ".venv/", "__pycache__/", "results/", "outputs/", "logs/",
            ".pytest_cache/", "*.pyc", ".DS_Store", "models/", "synthetic_data/"
        ]
        
        # Check if rsync is available
        try:
            rsync_available = subprocess.run(["rsync", "--version"], capture_output=True).returncode == 0
        except FileNotFoundError:
            rsync_available = False

        if rsync_available:
            exclude_args = [f"--exclude={e}" for e in exclude]
            # Use rsync to push local changes (including uncommitted)
            cmd = ["rsync", "-avz", "--delete"] + exclude_args + ["./", f"{host}:{remote_dir}/"]
            subprocess.run(cmd)
        else:
            # Fallback to scp (manual exclude is harder, so we just copy core directories or everything)
            print("rsync not found, using scp (note: this is less efficient and doesn't support easy excludes)")
            # For simplicity, we copy the current directory but we'll try to avoid the big folders
            # A better way is to copy src, scripts, config, and main.py individually
            for folder in ["src", "scripts", "config"]:
                subprocess.run(["scp", "-r", folder, f"{host}:{remote_dir}/"])
            subprocess.run(["scp", "main.py", f"{host}:{remote_dir}/"])
            if os.path.exists("requirements.txt"):
                subprocess.run(["scp", "requirements.txt", f"{host}:{remote_dir}/"])
    
    # 3. Pip install requirements
    print("Updating requirements on remote...")
    run_remote(cfg, f"cd {remote_dir} && ./.venv/bin/pip install -r requirements.txt")
    print("Push complete.")

def submit(cfg, experiments, group_name=None, experiments_per_job=None, script="main.py", remote_submit=False, mem_override=None):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    if group_name is None:
        group_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if remote_submit:
        # 1. Write all experiments to a local file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, newline='\n') as tmp:
            for exp in experiments:
                tmp.write(exp + "\n")
            tmp_path = tmp.name
        
        # 2. Upload the file to remote
        remote_file = f"{remote_dir}/logs/experiments_{group_name}.txt"
        run_remote(cfg, f"mkdir -p {remote_dir}/logs")
        subprocess.run(["scp", tmp_path, f"{host}:{remote_file}"])
        os.remove(tmp_path)
        
        # 3. Trigger remote submit
        print(f"Triggering remote submission for {len(experiments)} experiments...")
        cmd = f"cd {remote_dir} && ./.venv/bin/python scripts/slurm_manager.py submit-local --file logs/experiments_{group_name}.txt --name {group_name} --script {script}"
        if experiments_per_job:
            cmd += f" --group {experiments_per_job}"
        if mem_override:
            cmd += f" --mem {mem_override}"
        
        res = run_remote(cfg, cmd)
        print(res.stdout)
        if res.stderr:
            print(f"Remote Errors:\n{res.stderr}")
        return

    # Local submission logic (either called locally or on remote)
    slurm_cfg = cfg['slurm_defaults']
    if experiments_per_job is None:
        experiments_per_job = slurm_cfg.get('cpus_per_task', 8)
    
    mem = mem_override if mem_override else slurm_cfg['mem']
    
    # Ensure directories exist
    os.makedirs(f"logs/{group_name}", exist_ok=True)
    os.makedirs("results", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    for i in range(0, len(experiments), experiments_per_job):
        chunk = experiments[i : i + experiments_per_job]
        job_name = f"{group_name}_{i//experiments_per_job}"
        
        overrides_path = f"logs/{group_name}/{job_name}_overrides.txt"
        with open(overrides_path, 'w', newline='\n') as f:
            for exp in chunk:
                if "experiment_name=" not in exp:
                    exp += f" experiment_name={group_name}"
                f.write(exp + "\n")
        
        script_content = [
            "#!/bin/bash",
            f"#SBATCH --job-name={job_name}",
            f"#SBATCH --partition={slurm_cfg['partition']}",
            f"#SBATCH --time={slurm_cfg['time']}",
            f"#SBATCH --nodes={slurm_cfg['nodes']}",
            f"#SBATCH --ntasks={slurm_cfg['ntasks']}",
            f"#SBATCH --cpus-per-task={slurm_cfg['cpus_per_task']}",
            f"#SBATCH --mem={mem}",
            f"#SBATCH --output=logs/{group_name}/%x_%j.out",
            f"#SBATCH --error=logs/{group_name}/%x_%j.err",
            "",
            f"cd {os.getcwd()}",
            f"export PYTHONPATH=$PYTHONPATH:. ",
            "export HYDRA_FULL_ERROR=1",
            "",
            f"./.venv/bin/python scripts/run_parallel_experiments.py --script {script} --workers {slurm_cfg['cpus_per_task']} --overrides_file {overrides_path}"
        ]
        
        script_name = f"submit_{job_name}.sh"
        with open(script_name, "w", newline='\n') as f:
            f.write("\n".join(script_content))
            
        res = subprocess.run(["sbatch", script_name], capture_output=True, text=True)
        print(f"Submitted job {job_name}: {res.stdout.strip()}")
        os.remove(script_name)

def status(cfg):
    host = cfg['host']
    print(f"--- Active Jobs for {host} ---")
    res = run_remote(cfg, "squeue -u $(whoami)")
    if res.stdout:
        print(res.stdout)
    else:
        print("No active jobs found.")
    
    print("--- Recent Job History (sacct) ---")
    res = run_remote(cfg, "sacct --format=JobID,JobName,State,ExitCode,TimeLimit,Elapsed -n -X | tail -n 20")
    if res.stdout:
        print(res.stdout)
    else:
        print("No history found.")

def pull(cfg, names=None, types=None):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    if not types:
        types = ["results", "outputs", "logs"]
    
    if not names:
        names = [""] # Pull everything in the type directory
    
    # Check if rsync is available
    try:
        rsync_available = subprocess.run(["rsync", "--version"], capture_output=True).returncode == 0
    except FileNotFoundError:
        rsync_available = False
    
    for t in types:
        for name in names:
            print(f"Pulling {t} {name}...")
            remote_path = f"{remote_dir}/{t}/"
            local_path = f"{t}/"
            
            if name:
                remote_path += f"{name}/"
                local_path += f"{name}/"
            
            os.makedirs(local_path, exist_ok=True)
            
            if rsync_available:
                # Use rsync for efficient transfer
                cmd = ["rsync", "-avz", "--progress", f"{host}:{remote_path}", local_path]
            else:
                # Fallback to scp (available on Windows 10+)
                # Note: scp -r follows different semantics than rsync with trailing slashes.
                # To pull the CONTENTS of the remote dir into the local dir:
                cmd = ["scp", "-r", f"{host}:{remote_path}*", local_path]
            
            print(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd)
    
    print("Pull complete.")

def clean(cfg):
    host = cfg['host']
    remote_dir = cfg['remote_dir']
    
    confirm = input(f"Are you sure you want to clean results and logs on {host}:{remote_dir}? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
        
    print(f"Cleaning results, outputs and logs on {host}...")
    run_remote(cfg, f"cd {remote_dir} && rm -rf results/* outputs/* logs/*")
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
        res = run_remote(cfg, find_cmd)
        out_pattern = res.stdout.strip()
        if not out_pattern:
            print(f"No logs found in {log_dir}")
            return
        err_pattern = out_pattern.replace(".out", ".err")

    print(f"Checking logs from {host}: {out_pattern}")
    
    res = run_remote(cfg, f"tail -n {lines} {out_pattern}")
    print(f"--- Tail of Output Log ({os.path.basename(out_pattern)}) ---")
    print(res.stdout)
    
    res = run_remote(cfg, f"tail -n {lines} {err_pattern}")
    print(f"--- Tail of Error Log ({os.path.basename(err_pattern)}) ---")
    print(res.stdout)

def main():
    parser = argparse.ArgumentParser(description="Slurm Experiment Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    push_parser = subparsers.add_parser("push", help="Push code to remote server")
    push_parser.add_argument("--git", action="store_true", help="Use git instead of rsync")
    
    submit_parser = subparsers.add_parser("submit", help="Submit experiments to Slurm")
    submit_parser.add_argument("experiments", nargs="*", help="Hydra overrides for each experiment")
    submit_parser.add_argument("--file", type=str, help="File containing experiments (one per line)")
    submit_parser.add_argument("--name", type=str, help="Name for the experiment group")
    submit_parser.add_argument("--group", type=int, help="Number of experiments per job")
    submit_parser.add_argument("--script", type=str, default="main.py", help="Script to run")
    submit_parser.add_argument("--mem", type=str, help="Memory limit override (e.g., 64G)")
    submit_parser.add_argument("--remote", action="store_true", default=True, help="Trigger submission on remote (default)")
    submit_parser.add_argument("--local", action="store_false", dest="remote", help="Submit from local machine (legacy mode)")
    
    # Internal command for remote execution
    local_submit_parser = subparsers.add_parser("submit-local", help="Internal command for remote execution")
    local_submit_parser.add_argument("--file", type=str)
    local_submit_parser.add_argument("--name", type=str)
    local_submit_parser.add_argument("--group", type=int)
    local_submit_parser.add_argument("--script", type=str)
    local_submit_parser.add_argument("--mem", type=str)

    status_parser = subparsers.add_parser("status", help="Check job status")
    
    pull_parser = subparsers.add_parser("pull", help="Pull results from remote")
    pull_parser.add_argument("--name", nargs="*", help="Specific group names or patterns to pull")
    pull_parser.add_argument("--results", action="store_true", help="Pull only results")
    pull_parser.add_argument("--outputs", action="store_true", help="Pull only outputs")
    pull_parser.add_argument("--logs", action="store_true", help="Pull only logs")
    
    clean_parser = subparsers.add_parser("clean", help="Clean results and logs on remote server")
    
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
        push(cfg, args.git)
    elif args.command == "submit":
        exps = args.experiments
        if args.file:
            with open(args.file, "r") as f:
                exps.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])
        if not exps:
            print("No experiments provided.")
            return
        submit(cfg, exps, args.name, args.group, args.script, args.remote, args.mem)
    elif args.command == "submit-local":
        exps = []
        if args.file:
            with open(args.file, "r") as f:
                exps.extend([line.strip() for line in f if line.strip() and not line.startswith("#")])
        submit(cfg, exps, args.name, args.group, args.script, remote_submit=False, mem_override=args.mem)
    elif args.command == "status":
        status(cfg)
    elif args.command == "pull":
        types = []
        if args.results: types.append("results")
        if args.outputs: types.append("outputs")
        if args.logs: types.append("logs")
        pull(cfg, args.name, types)
    elif args.command == "clean":
        clean(cfg)
    elif args.command == "logs":
        logs(cfg, args.name, args.lines, args.job_id)

if __name__ == "__main__":
    main()
