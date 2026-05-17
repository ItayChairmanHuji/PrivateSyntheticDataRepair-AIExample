import subprocess
import sys
import os
from pathlib import Path

def generate_training_experiments():
    datasets = ["adult", "census", "compas", "tax"]
    engines = ["aim", "mst"]
    epsilons = [0.001] + [round(0.1 * i, 1) for i in range(1, 11)]
    
    overrides_list = []
    
    for ds in datasets:
        for engine in engines:
            for eps in epsilons:
                override = (
                    f"loading={ds} "
                    f"synthesizing={engine} "
                    f"synthesizing.epsilon={eps} "
                    f"experiment_name=train_{ds}_{engine}_eps{eps}"
                )
                overrides_list.append(override)
                
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch training sweep for AIM and MST.")
    parser.add_argument("--local", action="store_true", help="Run locally instead of Slurm")
    parser.add_argument("--workers", type=int, default=4, help="Local workers")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--group", type=int, default=4, help="Number of experiments per Slurm job")
    
    args = parser.parse_args()
    
    overrides = generate_training_experiments()
    print(f"Generated {len(overrides)} training experiments.")
    
    if args.dry_run:
        for o in overrides[:5]:
            print(o)
        print("...")
        return

    if args.local:
        with open("temp_train_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        subprocess.run([sys.executable, "scripts/run_parallel_experiments.py", "--script", "scripts/train_sn_model.py", "--workers", str(args.workers), "--overrides_file", "temp_train_overrides.txt"])
        os.remove("temp_train_overrides.txt")
    else:
        # First push code to remote
        print("Pushing code to remote...")
        subprocess.run([sys.executable, "scripts/slurm_manager.py", "push"])
        
        with open("slurm_train_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        
        cmd = [sys.executable, "scripts/slurm_manager.py", "submit", "--file", "slurm_train_overrides.txt", "--script", "scripts/train_sn_model.py", "--name", "train_sweep"]
        if args.group:
            cmd += ["--group", str(args.group)]
            
        print(f"Submitting to Slurm via slurm_manager (group size: {args.group})...")
        subprocess.run(cmd)
        os.remove("slurm_train_overrides.txt")

if __name__ == "__main__":
    main()
