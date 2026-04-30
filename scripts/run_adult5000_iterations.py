import subprocess
import sys
from pathlib import Path

# Add the project root to path so we can import slurm_manager if needed
# But it's easier to just call it via subprocess

def run_experiment():
    iterations = [10, 20, 30, 50, 100, 150, 200, 300, 500]
    seeds = [42, 43, 44]
    repairers = [
        "repairing=ilp repairing.use_marginals=True experiment_name=adult5000_iters_ilp_marginals",
        "repairing=ilp repairing.use_marginals=False experiment_name=adult5000_iters_ilp_no_marginals",
        "repairing=classic_vc experiment_name=adult5000_iters_classic_vc",
        "repairing=vanilla_vc experiment_name=adult5000_iters_vanilla_vc",
        "repairing=weighted_vc experiment_name=adult5000_iters_weighted_vc"
    ]
    
    overrides_list = []
    
    for iters in iterations:
        for seed in seeds:
            for repairer_base in repairers:
                override = (
                    f"loading.name=adult5000 "
                    f"synthesizing.num_of_iterations={iters} "
                    f"synthesizing.seed={seed} "
                    f"{repairer_base}"
                )
                overrides_list.append(override)
    
    print(f"Total experiments to submit: {len(overrides_list)}")
    
    # We submit in chunks to avoid too long command lines
    chunk_size = 10
    for i in range(0, len(overrides_list), chunk_size):
        chunk = overrides_list[i:i + chunk_size]
        cmd = [sys.executable, "scripts/slurm_manager.py", "submit"] + chunk
        print(f"Submitting chunk {i//chunk_size + 1}...")
        subprocess.run(cmd)

if __name__ == "__main__":
    run_experiment()
