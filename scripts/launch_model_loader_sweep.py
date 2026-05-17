import subprocess
import sys
import os
from pathlib import Path

def generate_model_loader_experiments():
    dataset = "tax"  # Finished all AIM and MST training
    engines = ["aim", "mst"]
    epsilons = [0.001] + [round(0.1 * i, 1) for i in range(1, 11)]
    repairers = ["weighted_vc", "classic_vc", "vanilla_vc"]
    alpha = 0.1
    k = 20
    size = 50000
    seed = 42
    
    overrides_list = []
    
    for engine in engines:
        for eps in epsilons:
            model_path = f"models/{dataset}_{engine}_eps{eps}.pkl"
            for repairer in repairers:
                # Distinguishable experiment name
                exp_name = f"eval_{dataset}_{engine}_eps{eps}_{repairer}_a{alpha}"
                
                override = (
                    f"loading={dataset} "
                    f"synthesizing=model_loader "
                    f"synthesizing.model_path={model_path} "
                    f"synthesizing.size={size} "
                    f"synthesizing.seed={seed} "
                    f"repairing={repairer} "
                    f"repairing.alpha={alpha} "
                    f"marginals_obtaining.k={k} "
                    f"experiment_name={exp_name}"
                )
                overrides_list.append(override)
                
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch full pipeline sweep using pre-trained models.")
    parser.add_argument("--local", action="store_true", help="Run locally instead of Slurm")
    parser.add_argument("--workers", type=int, default=4, help="Local workers")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--group", type=int, default=4, help="Number of experiments per Slurm job")
    
    args = parser.parse_args()
    
    overrides = generate_model_loader_experiments()
    print(f"Generated {len(overrides)} pipeline experiments.")
    
    if args.dry_run:
        for o in overrides[:5]:
            print(o)
        print("...")
        return

    if args.local:
        with open("temp_eval_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        subprocess.run([sys.executable, "scripts/run_parallel_experiments.py", "--workers", str(args.workers), "--overrides_file", "temp_eval_overrides.txt"])
        os.remove("temp_eval_overrides.txt")
    else:
        # First push code to remote
        print("Pushing code to remote...")
        subprocess.run([sys.executable, "scripts/slurm_manager.py", "push"])
        
        with open("slurm_eval_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        
        cmd = [sys.executable, "scripts/slurm_manager.py", "submit", "--file", "slurm_eval_overrides.txt", "--name", "model_loader_sweep"]
        if args.group:
            cmd += ["--group", str(args.group)]
            
        print(f"Submitting to Slurm via slurm_manager (group size: {args.group})...")
        subprocess.run(cmd)
        os.remove("slurm_eval_overrides.txt")

if __name__ == "__main__":
    main()
