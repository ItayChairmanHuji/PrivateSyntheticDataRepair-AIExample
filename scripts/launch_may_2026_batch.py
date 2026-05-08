
import subprocess
import sys
import os
from pathlib import Path

def generate_experiments(test_mode=False):
    if test_mode:
        datasets = ["adult"]
        models = ["mst"]
        repairers = {"weighted_vc": "repairing=weighted_vc"}
        seeds = [42]
    else:
        datasets = ["adult", "census", "compas", "tax"]
        models = ["aim", "mst", "patectgan"]
        repairers = {
            "weighted_vc": "repairing=weighted_vc",
            "vanilla_vc": "repairing=vanilla_vc",
            "classic_vc": "repairing=classic_vc",
            "ilp_marginals": "repairing=ilp repairing.use_marginals=True",
            "ilp_no_marginals": "repairing=ilp repairing.use_marginals=False"
        }
        seeds = [42, 43, 44]
    
    overrides_list = []
    
    for ds in datasets:
        for model in models:
            for rep_name, rep_base in repairers.items():
                for seed in seeds:
                    override = (
                        f"loading.name={ds} "
                        f"synthesizing=model_loader "
                        f"synthesizing.model_path=models/{ds}_{model}.pkl "
                        f"synthesizing.size=1000 "
                        f"synthesizing.seed={seed} "
                        f"marginals_obtaining.k=20 "
                        f"marginals_obtaining.selection_budget=0.5 "
                        f"marginals_obtaining.generation_budget=0.5 "
                        f"{rep_base} "
                        f"repairing.alpha=0.5 "
                        f"experiment_name=may_2026_batch"
                    )
                    overrides_list.append(override)

    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch the May 2026 experiment batch.")
    parser.add_argument("--local", action="store_true", help="Run locally instead of Slurm")
    parser.add_argument("--workers", type=int, default=4, help="Local workers")
    parser.add_argument("--dry-run", action="store_true", help="Just print the overrides")
    parser.add_argument("--test", action="store_true", help="Run a single test experiment")
    
    args = parser.parse_args()
    
    overrides = generate_experiments(test_mode=args.test)
    print(f"Generated {len(overrides)} experiments.")
    
    if args.dry_run:
        for o in overrides:
            print(o)
        return

    if args.local:
        with open("temp_overrides_may2026.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        subprocess.run([sys.executable, "scripts/run_parallel_experiments.py", "--workers", str(args.workers), "--overrides_file", "temp_overrides_may2026.txt"])
        os.remove("temp_overrides_may2026.txt")
    else:
        # Push changes to remote first (as per AGENT.md)
        # print("Pushing code to remote...")
        # subprocess.run([sys.executable, "scripts/slurm_manager.py", "push"])
        
        with open("slurm_overrides_may2026.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        
        # User requested: "Each experiment should be on it's own slurm job."
        # This means group size = 1
        cmd = [sys.executable, "scripts/slurm_manager.py", "submit", "--file", "slurm_overrides_may2026.txt", "--group", "1", "--name", "may_2026_batch"]
            
        print(f"Submitting to Slurm via slurm_manager (group size: 1)...")
        subprocess.run(cmd)
        os.remove("slurm_overrides_may2026.txt")

if __name__ == "__main__":
    main()
