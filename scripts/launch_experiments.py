import subprocess
import sys
import os
from pathlib import Path

def generate_experiments(test_mode=False):
    if test_mode:
        datasets = ["adult100"]
        repairers = {"weighted_vc": "repairing=weighted_vc"}
        seeds = [42]
        sweeps_to_run = ["alpha"] # Just one sweep for testing
    else:
        datasets = ["adult", "census", "compas", "tax"]
        repairers = {
            "weighted_vc": "repairing=weighted_vc",
            "vanilla_vc": "repairing=vanilla_vc",
            "classic_vc": "repairing=classic_vc",
            "ilp_marginals": "repairing=ilp repairing.use_marginals=True",
            "ilp_no_marginals": "repairing=ilp repairing.use_marginals=False"
        }
        seeds = [42, 43, 44, 45, 46, 47, 48, 49]
        sweeps_to_run = ["iters", "k", "sel_budget", "gen_budget", "alpha"]
    
    # Default values
    defaults = {
        "iters": 100,
        "k": 20,
        "sel_budget": 0.5,
        "gen_budget": 0.5,
        "alpha": 0.5
    }
    
    # Parameter sweeps
    sweeps = {
        "iters": [10, 50, 100, 200, 500],
        "k": [5, 10, 20, 50, 100],
        "sel_budget": [0.1, 0.3, 0.5, 0.7, 0.9],
        "gen_budget": [0.1, 0.3, 0.5, 0.7, 0.9],
        "alpha": [0.1, 0.3, 0.5, 0.7, 0.9]
    }
    
    overrides_list = []
    
    for ds in datasets:
        for rep_name, rep_base in repairers.items():
            for seed in seeds:
                # Base Override with ALL defaults
                base_override = (
                    f"loading.name={ds} "
                    f"synthesizing.seed={seed} "
                    f"{rep_base} "
                    f"synthesizing.num_of_iterations={defaults['iters']} "
                    f"marginals_obtaining.k={defaults['k']} "
                    f"marginals_obtaining.selection_budget={defaults['sel_budget']} "
                    f"marginals_obtaining.generation_budget={defaults['gen_budget']} "
                    f"repairing.alpha={defaults['alpha']} "
                    f"experiment_name=grid_{ds}_{rep_name}"
                )
                
                # 1. Always add the default run
                overrides_list.append(base_override)
                
                if test_mode and ds == "adult100":
                    # For test mode, we might want to skip some sweeps or do them all
                    pass

                # 2. Sweeps - each modifies EXACTLY ONE parameter from the base_override
                if "iters" in sweeps_to_run:
                    for val in sweeps["iters"]:
                        if val == defaults["iters"]: continue
                        overrides_list.append(base_override.replace(f"synthesizing.num_of_iterations={defaults['iters']}", f"synthesizing.num_of_iterations={val}"))
                
                if "k" in sweeps_to_run:
                    for val in sweeps["k"]:
                        if val == defaults["k"]: continue
                        overrides_list.append(base_override.replace(f"marginals_obtaining.k={defaults['k']}", f"marginals_obtaining.k={val}"))
                
                if "sel_budget" in sweeps_to_run:
                    for val in sweeps["sel_budget"]:
                        if val == defaults["sel_budget"]: continue
                        # Explicitly keep gen_budget at default while changing sel_budget
                        overrides_list.append(base_override.replace(f"marginals_obtaining.selection_budget={defaults['sel_budget']}", f"marginals_obtaining.selection_budget={val}"))
                
                if "gen_budget" in sweeps_to_run:
                    for val in sweeps["gen_budget"]:
                        if val == defaults["gen_budget"]: continue
                        # Explicitly keep sel_budget at default while changing gen_budget
                        overrides_list.append(base_override.replace(f"marginals_obtaining.generation_budget={defaults['gen_budget']}", f"marginals_obtaining.generation_budget={val}"))
                
                if "alpha" in sweeps_to_run:
                    for val in sweeps["alpha"]:
                        if val == defaults["alpha"]: continue
                        overrides_list.append(base_override.replace(f"repairing.alpha={defaults['alpha']}", f"repairing.alpha={val}"))

    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch the full experiment grid.")
    parser.add_argument("--local", action="store_true", help="Run locally instead of Slurm")
    parser.add_argument("--workers", type=int, default=4, help="Local workers")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--test", action="store_true", help="Run a single test experiment")
    parser.add_argument("--group", type=int, help="Number of experiments per Slurm job")
    
    args = parser.parse_args()
    
    overrides = generate_experiments(test_mode=args.test)
    print(f"Generated {len(overrides)} experiments.")
    
    if args.dry_run:
        return

    if args.local:
        with open("temp_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        subprocess.run([sys.executable, "scripts/run_parallel_experiments.py", "--workers", str(args.workers), "--overrides_file", "temp_overrides.txt"])
        os.remove("temp_overrides.txt")
    else:
        with open("slurm_overrides.txt", "w") as f:
            for o in overrides:
                f.write(o + "\n")
        
        cmd = [sys.executable, "scripts/slurm_manager.py", "submit", "--file", "slurm_overrides.txt"]
        if args.group:
            cmd += ["--group", str(args.group)]
            
        print(f"Submitting to Slurm via slurm_manager (group size: {args.group or 'default'})...")
        subprocess.run(cmd)
        os.remove("slurm_overrides.txt")

if __name__ == "__main__":
    main()
