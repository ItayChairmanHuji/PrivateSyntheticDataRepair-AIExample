import os
import subprocess
from pathlib import Path
import json

def get_existing_results():
    # Use SSH to get the list of result files on the remote
    cmd = ["ssh", "snorlax-login", "find ~/final_research/results/ -name 'result_*.json'"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return set(res.stdout.splitlines())

def generate_all_overrides():
    from scripts.launch_experiments import generate_experiments
    return generate_experiments(test_mode=False)

def check_missing():
    all_overrides = generate_all_overrides()
    existing_results = get_existing_results()
    
    # Map experiment_name and parameters to hash if possible, 
    # but the filenames contain a hash of the overrides.
    # Let's try to simulate the hashing logic or check if the experiment name is in the path.
    
    missing = []
    for override in all_overrides:
        # The experiment_name=grid_{ds}_{rep_name}
        # The result filename is result_{ds}_{hash}.json
        # The directory is results/grid_{ds}_{rep_name}
        
        # This is complex because we don't have the hashing logic easily available.
        # Alternative: run a script ON THE REMOTE that checks for each override if the result exists.
        pass

if __name__ == "__main__":
    # check_missing()
    pass
