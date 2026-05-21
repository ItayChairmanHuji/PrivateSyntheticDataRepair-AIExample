import subprocess
import argparse
import os
import json
import pandas as pd
from pathlib import Path

# Configuration
REMOTE_HOST = "snorlax-login"
REMOTE_DIR = "~/final_research"

def run_command(cmd):
    print(f"Executing: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def sync_results(experiment_group, use_zip=True):
    root = Path(__file__).resolve().parent.parent.parent
    local_output_base = root / "outputs" / experiment_group
    local_output_base.mkdir(parents=True, exist_ok=True)

    print(f"--- Step 1: Syncing '{experiment_group}' from {REMOTE_HOST} ---")
    
    if use_zip:
        zip_name = f"{experiment_group}_results.zip"
        remote_zip = f"{REMOTE_DIR}/{zip_name}"
        
        # 1. Zip on remote
        print(f"Zipping results on remote: {remote_zip}")
        # Note: we exclude private_data.csv to keep it light if needed, or include everything
        zip_cmd = f"ssh {REMOTE_HOST} 'cd {REMOTE_DIR} && zip -r {zip_name} outputs/{experiment_group}'"
        run_command(zip_cmd)
        
        # 2. Pull zip
        print(f"Pulling {zip_name}...")
        pull_cmd = f"scp {REMOTE_HOST}:{remote_zip} {root}/{zip_name}"
        run_command(pull_cmd)
        
        # 3. Unzip locally
        print(f"Extracting {zip_name} locally...")
        # Using python zipfile for cross-platform unzip
        import zipfile
        with zipfile.ZipFile(root / zip_name, 'r') as zip_ref:
            zip_ref.extractall(root)
            
        # 4. Cleanup
        os.remove(root / zip_name)
        run_command(f"ssh {REMOTE_HOST} 'rm {remote_zip}'")
    else:
        # Fallback to rsync/scp
        remote_path = f"{REMOTE_HOST}:{REMOTE_DIR}/outputs/{experiment_group}/"
        local_path = f"{local_output_base}/"
        try:
            rsync_cmd = f"rsync -avzP {remote_path} {local_path}"
            run_command(rsync_cmd)
        except Exception:
            print("rsync failed or not found, falling back to scp...")
            scp_cmd = f"scp -r {remote_path}* {local_path}"
            run_command(scp_cmd)

    print(f"--- Step 2: Aggregating Results ---")
    all_results = []
    
    # Walk through the local synced directory to find all .json results
    # Trace structure: [group]/exp_XXX/[stage]/output/result_*.json
    for exp_dir in local_output_base.iterdir():
        if exp_dir.is_dir() and exp_dir.name.startswith("exp_"):
            # Check s05_evaluating subfolder
            eval_dir = exp_dir / "s05_evaluating"
            if eval_dir.exists():
                for result_file in eval_dir.rglob("result_*.json"):
                    try:
                        with open(result_file, 'r') as f:
                            data = json.load(f)
                            all_results.append(data)
                    except Exception as e:
                        print(f"Error reading {result_file}: {e}")

    if all_results:
        df = pd.DataFrame(all_results)
        # Ensure we have some identifying columns if they are missing
        summary_path = root / "s07_sync" / "output" / f"{experiment_group}_summary.csv"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(summary_path, index=False)
        print(f"Successfully aggregated {len(all_results)} results into {summary_path}")
    else:
        print("No results found to aggregate.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", type=str, required=True, help="Experiment group name (e.g., experiment_1_generation)")
    args = parser.parse_args()
    
    sync_results(args.blueprint)
