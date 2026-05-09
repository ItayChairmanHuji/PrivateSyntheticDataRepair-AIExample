import subprocess
import sys
import os
from pathlib import Path

def generate_alpha_sweep_v2():
    datasets = ["adult", "census", "compas", "tax"]
    models = ["aim", "mst", "patectgan"]
    
    # Combined alphas: 0 to 0.1 in 0.01 steps, and 0.2 to 1.0 in 0.1 steps
    alphas_fine = [round(i * 0.01, 2) for i in range(11)] 
    alphas_coarse = [round(i * 0.1, 1) for i in range(2, 11)]
    alphas = sorted(list(set(alphas_fine + alphas_coarse)))
    
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
                    f"experiment_name=alpha_sweep_v2_{ds}_{model}_a{alpha}"
                )
                overrides_list.append(override)
    
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch the Alpha Sweep V2.")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--canary", action="store_true", help="Run a single canary experiment on remote")
    
    args = parser.parse_args()
    
    overrides = generate_alpha_sweep_v2()
    print(f"Generated {len(overrides)} experiments.")
    
    if args.dry_run:
        for o in overrides[:5]:
            print(o)
        return

    if args.canary:
        canary_exp = overrides[len(overrides)//2] 
        canary_exp = canary_exp.replace("experiment_name=", "experiment_name=canary_v2_")
        print(f"Running canary experiment: {canary_exp}")
        
        # Push code
        print("Pushing code to remote...")
        subprocess.run([sys.executable, "scripts/slurm_manager.py", "push", "--git"])
        
        # Run on remote
        print("Running on remote...")
        import yaml
        with open("config/remote/slurm.yaml", "r") as f:
            cfg = yaml.safe_load(f)
        remote_dir = cfg['remote_dir']
        host = cfg['host']
        
        remote_cmd = f"cd {remote_dir} && ./.venv/bin/python main.py {canary_exp}"
        subprocess.run(["ssh", host, remote_cmd])
        return

    with open("alpha_sweep_v2_overrides.txt", "w") as f:
        for o in overrides:
            f.write(o + "\n")
    
    # Push code
    print("Pushing code to remote...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "push", "--git"])
    
    # Submit to Slurm
    print("Submitting to Slurm...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "submit", "--file", "alpha_sweep_v2_overrides.txt", "--name", "alpha_sweep_v2_may9", "--group", "10"])
    
    os.remove("alpha_sweep_v2_overrides.txt")

if __name__ == "__main__":
    main()
