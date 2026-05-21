import subprocess
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

def launch_experiments():
    datasets = ["adult", "census", "compas", "tax"]
    engines = ["aim", "mst"]
    epsilons = [0.1, 0.5, 1.0]
    
    experiment_group = "adaptive_alpha_comparison_v1"
    
    # We will generate a list of commands to run
    # Each command will run the pipeline with different repairer configurations
    commands = []
    
    for ds in datasets:
        for eng in engines:
            for eps in epsilons:
                # Base config for this (dataset, engine, eps) triplet
                # We use model_loader to ensure consistent synthetic data
                common_overrides = [
                    f"loading={ds}",
                    f"synthesizing=model_loader",
                    f"synthesizing.model_path=models/{ds}_{eng}_eps{eps}.pkl",
                ]
                
                # 1. Vanilla VC (Standard Greedy)
                vanilla_exp_name = f"{experiment_group}/{ds}_{eng}_eps{eps}_vanilla"
                commands.append(" ".join(common_overrides + [
                    f"repairing=vanilla_vc", 
                    f"experiment_name={vanilla_exp_name}",
                    f"hydra.run.dir=outputs/{vanilla_exp_name}"
                ]))
                
                # 2. Classic VC (Weighted but fixed alpha=0.5)
                classic_exp_name = f"{experiment_group}/{ds}_{eng}_eps{eps}_classic"
                commands.append(" ".join(common_overrides + [
                    f"repairing=weighted_vc", 
                    f"repairing.alpha=0.5", 
                    f"experiment_name={classic_exp_name}",
                    f"hydra.run.dir=outputs/{classic_exp_name}"
                ]))
                
                # 3. Adaptive Alpha VC
                adaptive_exp_name = f"{experiment_group}/{ds}_{eng}_eps{eps}_adaptive"
                commands.append(" ".join(common_overrides + [
                    f"repairing=weighted_vc", 
                    f"repairing.use_adaptive_alpha=True", 
                    f"experiment_name={adaptive_exp_name}",
                    f"hydra.run.dir=outputs/{adaptive_exp_name}"
                ]))

    # Write commands to a file for slurm_manager
    exp_file = f"logs/experiments_{experiment_group}.txt"
    os.makedirs("logs", exist_ok=True)
    with open(exp_file, "w") as f:
        for cmd in commands:
            f.write(cmd + "\n")
            
    print(f"Generated {len(commands)} experiments in {exp_file}")
    
    # Push and Submit
    print("Pushing code to remote...")
    subprocess.run(["python", "scripts/slurm_manager.py", "push"])
    
    print("Submitting to Slurm...")
    # Use 64G per job, 1 experiment per job for safety
    subprocess.run([
        "python", "scripts/slurm_manager.py", "submit", 
        "--file", exp_file, 
        "--name", experiment_group, 
        "--group", "1", 
        "--mem", "64G"
    ])

if __name__ == "__main__":
    launch_experiments()
