import subprocess
import sys
import os
from pathlib import Path

def generate_graph_experiments():
    datasets = ["adult", "census", "compas", "tax"]
    engines = ["aim", "mst"]
    epsilons = [0.001] + [round(0.1 * i, 1) for i in range(1, 11)]
    
    overrides_list = []
    
    for ds in datasets:
        for engine in engines:
            for eps in epsilons:
                # We use model_loader to load the pre-trained models
                model_path = f"models/{ds}_{engine}_eps{eps}.pkl"
                override = (
                    f"loading={ds} "
                    f"loading.size=50000 "
                    f"synthesizing=model_loader "
                    f"synthesizing.model_path={model_path} "
                    f"experiment_name=graph_{ds}_{engine}_eps{eps}"
                )
                overrides_list.append(override)
                
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch graph generation sweep.")
    parser.add_argument("--local", action="store_true", help="Run locally instead of Slurm")
    parser.add_argument("--workers", type=int, default=4, help="Local workers")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--group", type=int, default=4, help="Number of experiments per Slurm job")
    parser.add_argument("--mem", type=str, help="Memory limit override")
    
    parser.add_argument("--datasets", nargs="*", help="Specific datasets to run")
    
    args = parser.parse_args()
    
    overrides = generate_graph_experiments()
    if args.datasets:
        overrides = [o for o in overrides if any(f"loading={ds} " in o for ds in args.datasets)]
    
    print(f"Generated {len(overrides)} graph generation experiments.")
    
    if args.dry_run:
        for o in overrides[:5]:
            print(o)
        print("...")
        return

    if args.local:
        with open("temp_graph_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        subprocess.run([sys.executable, "scripts/run_parallel_experiments.py", "--script", "scripts/generate_conflict_graphs.py", "--workers", str(args.workers), "--overrides_file", "temp_graph_overrides.txt"])
        os.remove("temp_graph_overrides.txt")
    else:
        # First push code to remote
        print("Pushing code to remote via zip...")
        subprocess.run([sys.executable, "scripts/slurm_manager.py", "push", "--zip"])
        
        with open("slurm_graph_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        
        # We need to specify the script to run in slurm_manager.py
        cmd = [sys.executable, "scripts/slurm_manager.py", "submit", "--file", "slurm_graph_overrides.txt", "--script", "scripts/generate_conflict_graphs.py", "--name", "graph_generation"]
        if args.group:
            cmd += ["--group", str(args.group)]
        if args.mem:
            cmd += ["--mem", args.mem]
            
        print(f"Submitting to Slurm via slurm_manager (group size: {args.group})...")
        subprocess.run(cmd)
        os.remove("slurm_graph_overrides.txt")

if __name__ == "__main__":
    main()
