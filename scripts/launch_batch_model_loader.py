import subprocess
import sys
import os
from pathlib import Path
import argparse

def generate_experiments(datasets):
    models = ["aim", "patectgan", "mst"]
    repairers = {
        "classic_vc": "repairing=classic_vc",
        "vanilla_vc": "repairing=vanilla_vc",
        "weighted_vc": "repairing=weighted_vc",
        "ilp_marginals": "repairing=ilp repairing.use_marginals=True",
        "ilp_no_marginals": "repairing=ilp repairing.use_marginals=False"
    }
    seeds = [42, 43, 44]
    
    overrides_list = []
    
    for ds in datasets:
        for model in models:
            for rep_name, rep_base in repairers.items():
                for seed in seeds:
                    # Construct overrides
                    override = (
                        f"loading.name={ds} "
                        f"loading.seed={seed} "
                        f"synthesizing=model_loader "
                        f"synthesizing.model_path=models/{ds}_{model}.pkl "
                        f"synthesizing.size=1000 "
                        f"synthesizing.seed={seed} "
                        f"marginals_obtaining.k=20 "
                        f"marginals_obtaining.seed={seed} "
                        f"{rep_base} "
                        f"experiment_name=batch_ml_{ds}_{model}_{rep_name}_s{seed}"
                    )
                    overrides_list.append(override)
    
    return overrides_list

def main():
    parser = argparse.ArgumentParser(description="Launch the model loader experiment batch.")
    parser.add_argument("--local", action="store_true", help="Run locally instead of Slurm")
    parser.add_argument("--workers", type=int, default=4, help="Local workers")
    parser.add_argument("--dry-run", action="store_true", help="Just print the experiments and exit")
    parser.add_argument("--group", type=int, default=10, help="Number of experiments per Slurm job")
    parser.add_argument("--datasets", type=str, default="adult,compas,census,tax", help="Comma separated list of datasets")
    
    args = parser.parse_args()
    datasets = args.datasets.split(",")
    
    overrides = generate_experiments(datasets)
    print(f"Generated {len(overrides)} experiments.")
    
    if args.dry_run:
        print("\nFirst 5 experiments:")
        for o in overrides[:5]:
            print(f"  {o}")
        print("\nLast 5 experiments:")
        for o in overrides[-5:]:
            print(f"  {o}")
        return

    if args.local:
        print(f"Running {len(overrides)} experiments locally with {args.workers} workers...")
        temp_file = "temp_batch_overrides.txt"
        with open(temp_file, "w") as f:
            for o in overrides:
                f.write(o + "\n")
        subprocess.run([sys.executable, "scripts/run_parallel_experiments.py", "--workers", str(args.workers), "--overrides_file", temp_file])
        os.remove(temp_file)
    else:
        print(f"Submitting {len(overrides)} experiments to Slurm (group size: {args.group})...")
        slurm_file = "slurm_batch_overrides.txt"
        with open(slurm_file, "w") as f:
            for o in overrides:
                f.write(o + "\n")
        
        cmd = [sys.executable, "scripts/slurm_manager.py", "submit", "--file", slurm_file, "--group", str(args.group)]
        subprocess.run(cmd)
        os.remove(slurm_file)

if __name__ == "__main__":
    main()
