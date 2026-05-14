import subprocess
import sys
import os
import yaml
from pathlib import Path

def generate_alpha_sweep():
    datasets = ["adult", "census", "compas", "tax"]
    models = ["aim", "mst"]
    
    # Alphas: 0 to 1.0 in 0.05 steps for better resolution in the new function
    alphas = [round(i * 0.05, 2) for i in range(21)]
    
    seed = 42
    size = 50000
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
                    f"experiment_name=weighted_updated_alpha_v4_{ds}_{model}_a{alpha}"
                )
                overrides_list.append(override)
    
    return overrides_list

def generate_epsilon_sweep():
    dataset = "tax" 
    engines = ["aim", "mst"]
    epsilons = [0.001] + [round(0.1 * i, 1) for i in range(1, 11)]
    alpha = 0.5 # Default alpha
    k = 20
    size = 50000
    seed = 42
    
    overrides_list = []
    
    for engine in engines:
        for eps in epsilons:
            model_path = f"models/{dataset}_{engine}_eps{eps}.pkl"
            # Distinguishable experiment name
            exp_name = f"weighted_updated_eps_v4_{dataset}_{engine}_eps{eps}_a{alpha}"
            
            override = (
                f"loading={dataset} "
                f"synthesizing=model_loader "
                f"synthesizing.model_path={model_path} "
                f"synthesizing.size={size} "
                f"synthesizing.seed={seed} "
                f"repairing=weighted_vc "
                f"repairing.alpha={alpha} "
                f"marginals_obtaining.k={k} "
                f"experiment_name={exp_name}"
            )
            overrides_list.append(override)
                
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Launch weighted update sweeps.")
    parser.add_argument("--dry-run", action="store_true", help="Just print the number of experiments")
    parser.add_argument("--canary", action="store_true", help="Run a single canary experiment on remote")
    parser.add_argument("--alpha", action="store_true", help="Launch alpha sweep")
    parser.add_argument("--epsilon", action="store_true", help="Launch epsilon sweep")
    
    args = parser.parse_args()
    
    if not args.alpha and not args.epsilon:
        print("Please specify --alpha, --epsilon or both.")
        return

    overrides = []
    if args.alpha:
        overrides.extend(generate_alpha_sweep())
    if args.epsilon:
        overrides.extend(generate_epsilon_sweep())
        
    print(f"Generated {len(overrides)} experiments.")
    
    if args.dry_run:
        for o in overrides[:10]:
            print(o)
        print("...")
        return

    if args.canary:
        # Pick one representative experiment
        canary_exp = [o for o in overrides if "weighted_vc" in o][0]
        canary_exp = canary_exp.replace("experiment_name=", "experiment_name=canary_weighted_v4_")
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

    group_name = "weighted_updated_may14"
    overrides_file = f"{group_name}_overrides.txt"
    with open(overrides_file, "w") as f:
        for o in overrides:
            f.write(o + "\n")
    
    # Push code
    print("Pushing code to remote...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "push", "--git"])
    
    # Submit to Slurm
    print("Submitting to Slurm...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "submit", "--file", overrides_file, "--name", group_name, "--group", "5"])
    
    os.remove(overrides_file)

if __name__ == "__main__":
    main()
