import subprocess
import sys
import os
from pathlib import Path

def generate_alpha_sweep():
    datasets = ["adult", "census", "compas", "tax"]
    models = ["aim", "mst", "patectgan"]
    # 10 values between 0 and 0.1, inclusive
    alphas = [round(i * 0.01, 2) for i in range(11)] 
    seed = 42
    size = 1000
    k = 20
    
    overrides_list = []
    
    for ds in datasets:
        for model in models:
            for alpha in alphas:
                override = (
                    f"loading={ds} "
                    f"synthesizing=model_loader "
                    f"synthesizing.model_path=models/{ds}_{model}.pkl "
                    f"synthesizing.size={size} "
                    f"marginals_obtaining.k={k} "
                    f"repairing=weighted_vc "
                    f"repairing.alpha={alpha} "
                    f"synthesizing.seed={seed} "
                    f"experiment_name=alpha_sweep_fine_{ds}_{model}_a{alpha}"
                )
                overrides_list.append(override)
    
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch the fine alpha sweep.")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--canary", action="store_true", help="Run a single canary experiment on remote")
    
    args = parser.parse_args()
    
    overrides = generate_alpha_sweep()
    print(f"Generated {len(overrides)} experiments.")
    
    if args.dry_run:
        for o in overrides[:5]:
            print(o)
        return

    if args.canary:
        canary_exp = overrides[len(overrides)//2] # Pick one from the middle
        # Prefix with canary_
        canary_exp = canary_exp.replace("experiment_name=", "experiment_name=canary_")
        print(f"Running canary experiment: {canary_exp}")
        
        # We need to make sure code is pushed first
        print("Pushing code to remote...")
        subprocess.run([sys.executable, "scripts/slurm_manager.py", "push"])
        
        # Run on remote
        print("Running on remote...")
        # Get config to know remote_dir
        import yaml
        with open("config/remote/slurm.yaml", "r") as f:
            cfg = yaml.safe_load(f)
        remote_dir = cfg['remote_dir']
        host = cfg['host']
        
        remote_cmd = f"cd {remote_dir} && ./.venv/bin/python main.py {canary_exp}"
        subprocess.run(["ssh", host, remote_cmd])
        return

    with open("alpha_sweep_fine_overrides.txt", "w") as f:
        for o in overrides:
            f.write(o + "\n")
    
    # Push code
    print("Pushing code to remote...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "push"])
    
    # Submit to Slurm
    print("Submitting to Slurm...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "submit", "--file", "alpha_sweep_fine_overrides.txt", "--name", "alpha_sweep_fine_may9", "--group", "10"])
    
    os.remove("alpha_sweep_fine_overrides.txt")

if __name__ == "__main__":
    main()
