import subprocess
import sys
import os
import yaml
from pathlib import Path

def generate_overrides():
    datasets = ["adult", "census", "compas", "tax"]
    models = ["aim", "mst"]
    eps = "0.5"
    
    # Alphas for sweep
    alphas_fine = [round(i * 0.01, 2) for i in range(11)] 
    alphas_coarse = [round(i * 0.1, 1) for i in range(2, 11)]
    alphas = sorted(list(set(alphas_fine + alphas_coarse)))
    
    # Repairers
    repairers = ["weighted_vc", "ilp", "classic_vc", "vanilla_vc"]
    
    seed = 42
    size = 50000
    k = 20
    
    overrides_list = []
    
    for ds in datasets:
        for model in models:
            for rep in repairers:
                for alpha in alphas:
                    override = (
                        f"loading={ds} "
                        f"synthesizing=model_loader "
                        f"synthesizing.model_path=models/{ds}_{model}_eps{eps}.pkl "
                        f"synthesizing.size={size} "
                        f"marginals_obtaining.k={k} "
                        f"repairing={rep} "
                        f"repairing.alpha={alpha} "
                        f"synthesizing.seed={seed} "
                        f"experiment_name=alpha_sweep_may2026_{ds}_{model}_{rep}_a{alpha}"
                    )
                    overrides_list.append(override)
    
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch the May 2026 Alpha Sweep.")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--canary", action="store_true", help="Run a single canary experiment on remote")
    
    args = parser.parse_args()
    
    overrides = generate_overrides()
    print(f"Generated {len(overrides)} experiments.")
    
    if args.dry_run:
        for o in overrides[:10]:
            print(o)
        print("...")
        for o in overrides[-10:]:
            print(o)
        return

    if args.canary:
        # Pick one representative experiment: adult, aim, weighted_vc, alpha=0.5
        canary_exp = [o for o in overrides if "adult" in o and "aim" in o and "weighted_vc" in o and "a0.5" in o][0]
        canary_exp = canary_exp.replace("experiment_name=", "experiment_name=canary_may2026_")
        print(f"Running canary experiment: {canary_exp}")
        
        # Push code
        print("Pushing code to remote...")
        subprocess.run([sys.executable, "scripts/slurm_manager.py", "push", "--git"])
        
        # Run on remote
        print("Running on remote...")
        with open("config/remote/slurm.yaml", "r") as f:
            cfg = yaml.safe_load(f)
        remote_dir = cfg['remote_dir']
        host = cfg['host']
        
        remote_cmd = f"cd {remote_dir} && ./.venv/bin/python main.py {canary_exp}"
        subprocess.run(["ssh", host, remote_cmd])
        return

    with open("alpha_sweep_may2026_overrides.txt", "w") as f:
        for o in overrides:
            f.write(o + "\n")
    
    # Push code
    print("Pushing code to remote...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "push", "--git"])
    
    # Submit to Slurm
    print("Submitting to Slurm...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "submit", "--file", "alpha_sweep_may2026_overrides.txt", "--name", "alpha_sweep_may2026", "--group", "5"])
    
    os.remove("alpha_sweep_may2026_overrides.txt")

if __name__ == "__main__":
    main()
