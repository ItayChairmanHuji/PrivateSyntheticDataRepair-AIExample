import os

def generate_noise_sweep():
    datasets = ["adult", "compas", "census", "tax"]
    repairers = {
        "weighted_vc": "repairing=weighted_vc",
        "vanilla_vc": "repairing=vanilla_vc",
        "classic_vc": "repairing=classic_vc",
        "ilp_marginals": "repairing=ilp repairing.use_marginals=True",
        "ilp_no_marginals": "repairing=ilp repairing.use_marginals=False"
    }
    seeds = [42, 43, 44]
    iterations = [50, 100, 200]
    
    overrides_list = []
    
    for ds in datasets:
        for rep_name, rep_cmd in repairers.items():
            for seed in seeds:
                for iters in iterations:
                    # Use the base_sweep experiment template
                    # Set hydra.run.dir to prevent collisions in parallel runs
                    exp_name = f"sweep_{ds}_{rep_name}_it{iters}_s{seed}"
                    override = (
                        f"experiment=base_sweep "
                        f"loading.name={ds} "
                        f"{rep_cmd} "
                        f"synthesizing.num_of_iterations={iters} "
                        f"loading.seed={seed} "
                        f"synthesizing.seed={seed} "
                        f"marginals_obtaining.seed={seed} "
                        f"experiment_name={exp_name} "
                        f"hydra.run.dir=outputs/{exp_name}"
                    )
                    overrides_list.append(override)
    
    return overrides_list

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate the noise iterations sweep.")
    parser.add_argument("--name", type=str, default="noise_sweep_v1", help="Name of the experiment group")
    args = parser.parse_args()
    
    overrides = generate_noise_sweep()
    print(f"Generated {len(overrides)} experiments for group '{args.name}'.")
    
    output_file = f"{args.name}.txt"
    with open(output_file, "w") as f:
        for o in overrides:
            f.write(o + "\n")
    
    print(f"Overrides written to {output_file}")
    print(f"\nTo deploy, run:")
    print(f"python scripts/slurm_manager.py submit --file {output_file} --name {args.name}")

if __name__ == "__main__":
    main()
