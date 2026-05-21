import subprocess
import argparse
import json
import pandas as pd
import os
from pathlib import Path

def sync_results(job_ids_path, output_dir):
    with open(job_ids_path, 'r') as f:
        job_info = json.load(f)
    
    group_name = job_info['group']
    print(f"Syncing results for group: {group_name}")
    
    # 1. Rsync results from remote
    # (Simplified for example)
    # subprocess.run(["rsync", "-avz", "host:remote_path/results/", f"{output_dir}/{group_name}/"])
    
    # 2. Aggregate
    all_results = []
    # Mock aggregation for example
    # In reality, walk through output_dir and find all result.json files
    
    print(f"Aggregated results into {output_dir}/aggregated_results.csv")
    # pd.DataFrame(all_results).to_csv(f"{output_dir}/aggregated_results.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_ids", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="icm_sandbox/07_result_syncing/output")
    args = parser.parse_args()
    sync_results(args.job_ids, args.output_dir)
