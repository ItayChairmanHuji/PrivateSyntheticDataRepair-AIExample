import os
import subprocess
import json
import hashlib
from scripts.launch_experiments import generate_experiments

def get_existing_results():
    """Returns a set of (dataset_name, experiment_name) tuples that have results."""
    # We'll just look at the directories under results/
    cmd = ["find", "results/", "-name", "result_*.json"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    
    existing = set()
    for line in res.stdout.splitlines():
        if not line: continue
        # results/grid_adult_weighted_vc/result_adult_012be64a.json
        parts = line.split('/')
        if len(parts) >= 3:
            exp_dir = parts[1] # grid_adult_weighted_vc
            existing.add(exp_dir)
            
    return existing

def main():
    all_overrides = generate_experiments(test_mode=False)
    existing_dirs = get_existing_results()
    
    # We want to find which OVERRIDES are missing.
    # Since we can't easily match result files to overrides (due to hash),
    # we'll use a simpler heuristic: if the experiment_name directory doesn't exist, 
    # or if we know it failed (like classic_vc).
    
    missing_overrides = []
    
    for override_str in all_overrides:
        # Extract experiment_name from override_str
        # experiment_name=grid_tax_weighted_vc
        parts = override_str.split()
        exp_name = next((p.split('=')[1] for p in parts if p.startswith('experiment_name=')), None)
        
        # Heuristic 1: If it's classic_vc or vanilla_vc, it definitely failed.
        if "repairing=classic_vc" in override_str or "repairing=vanilla_vc" in override_str:
            missing_overrides.append(override_str)
            continue
            
        # Heuristic 2: If the directory doesn't exist at all.
        if exp_name not in existing_dirs:
            missing_overrides.append(override_str)
            continue
            
        # Heuristic 3: Check if number of results matches expected seeds? 
        # (Total seeds = 8 default + 1 baseline? Actually it's 8 seeds for each param combo)
        # This is getting complex. Let's start by just running the ones we KNOW failed.
    
    print(f"Total experiments: {len(all_overrides)}")
    print(f"Missing/Failed experiments: {len(missing_overrides)}")
    
    with open("missing_overrides.txt", "w") as f:
        for m in missing_overrides:
            f.write(m + "\n")

if __name__ == "__main__":
    main()
