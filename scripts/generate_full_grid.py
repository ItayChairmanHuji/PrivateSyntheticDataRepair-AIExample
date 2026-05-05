
def generate():
    datasets = ["adult", "census", "compas", "tax"]
    engines = ["mst", "aim", "patectgan"]
    seeds = [42, 43, 44]
    repairers = {
        "weighted_vc": "repairing=weighted_vc",
        "vanilla_vc": "repairing=vanilla_vc",
        "classic_vc": "repairing=classic_vc",
        "ilp_marginals": "repairing=ilp repairing.use_marginals=True",
        "ilp_no_marginals": "repairing=ilp repairing.use_marginals=False"
    }
    
    overrides = []
    for ds in datasets:
        for eng in engines:
            model_path = f"models/{ds}_{eng}.pkl"
            for seed in seeds:
                for rep_name, rep_base in repairers.items():
                    o = (
                        f"loading.name={ds} "
                        f"loading.size=5000 "
                        f"loading.seed={seed} "
                        f"synthesizing=model_loader "
                        f"synthesizing.model_path={model_path} "
                        f"synthesizing.size=5000 "
                        f"synthesizing.seed={seed} "
                        f"{rep_base} "
                        f"marginals_obtaining.k=20 "
                        f"repairing.alpha=0.5 "
                        f"experiment_name=full_repair_grid"
                    )
                    overrides.append(o)
    return overrides

if __name__ == "__main__":
    overrides = generate()
    with open("full_grid_overrides.txt", "w") as f:
        for o in overrides:
            f.write(o + "\n")
    print(f"Generated {len(overrides)} experiments.")
