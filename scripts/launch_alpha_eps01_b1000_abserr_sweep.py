import os
import subprocess
import sys
import yaml

def generate_alpha_eps01_b1000_abserr_sweep():
    datasets = ["adult", "census", "compas", "tax"]
    models = ["aim", "mst"]
    alphas = [round(i * 0.05, 2) for i in range(21)]
    eps = 0.1
    seed = 42
    size = 50000
    k = 20
    budget = 1000

    overrides_list = []

    for ds in datasets:
        for model in models:
            for alpha in alphas:
                model_path = f"models/{ds}_{model}_eps{eps}.pkl"
                # Use distinguishable prefix
                exp_name = f"alpha_eps01_b1000_abserr_{ds}_{model}_a{alpha}"
                override = (
                    f"loading={ds} "
                    f"synthesizing=model_loader "
                    f"synthesizing.model_path={model_path} "
                    f"synthesizing.size={size} "
                    f"synthesizing.seed={seed} "
                    f"repairing=weighted_vc "
                    f"repairing.alpha={alpha} "
                    f"marginals_obtaining.k={k} "
                    f"marginals_obtaining.selection_budget={budget} "
                    f"marginals_obtaining.generation_budget={budget} "
                    f"experiment_name={exp_name}"
                )
                overrides_list.append(override)

    return overrides_list

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Launch alpha sweep with eps=0.1, budget=1000, and Absolute Error weights.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Just print the number of experiments"
    )

    args = parser.parse_args()

    overrides = generate_alpha_eps01_b1000_abserr_sweep()

    print(f"Generated {len(overrides)} absolute error experiments.")

    if args.dry_run:
        for o in overrides[:10]:
            print(o)
        print("...")
        return

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    group_name = f"alpha_eps01_b1000_abserr_{timestamp}"
    overrides_file = f"{group_name}_overrides.txt"
    with open(overrides_file, "w") as f:
        for o in overrides:
            f.write(o + "\n")

    # Push code
    print("Pushing updated code to remote...")
    subprocess.run([sys.executable, "scripts/slurm_manager.py", "push", "--git"])

    # Submit to Slurm
    print("Submitting absolute error sweep to Slurm...")
    subprocess.run(
        [
            sys.executable,
            "scripts/slurm_manager.py",
            "submit",
            "--file",
            overrides_file,
            "--name",
            group_name,
            "--group",
            "5",
        ]
    )

    os.remove(overrides_file)

if __name__ == "__main__":
    main()
