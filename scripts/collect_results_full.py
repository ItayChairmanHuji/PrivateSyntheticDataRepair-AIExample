import json
import os

import pandas as pd


def collect_results(dataset_prefix):
    base_results_dir = "results"
    algorithms = [
        "ilp_marginals",
        "ilp_no_marginals",
        "classic_vc",
        "vanilla_vc",
        "weighted_vc",
    ]
    experiments = [f"{dataset_prefix}_{alg}" for alg in algorithms]

    summary = []

    for exp in experiments:
        exp_dir = os.path.join(base_results_dir, exp)
        if not os.path.exists(exp_dir):
            continue

        files = [f for f in os.listdir(exp_dir) if f.endswith(".json")]
        if not files:
            continue

        files.sort(
            key=lambda x: os.path.getmtime(os.path.join(exp_dir, x)), reverse=True
        )
        latest_file = files[0]

        with open(os.path.join(exp_dir, latest_file), "r") as f:
            data = json.load(f)

        dr = data.get("deletion_ratio", {})
        ratio = dr.get("ratio", 0) if isinstance(dr, dict) else 0

        me = data.get("marginals_error", {})
        rep_me = me.get("repaired_avg", 0) if isinstance(me, dict) else 0

        metrics = {
            "Algorithm": exp.replace(f"{dataset_prefix}_", ""),
            "Del Ratio": f"{ratio:.3f}",
            "Avg TVD": f"{data.get('tvd', {}).get('avg_tvd', 0):.3f}",
            "Marg Error": f"{rep_me:.3f}",
            "Repair Time (s)": f"{data.get('runtimes', {}).get('repairing', 0):.3f}",
        }
        summary.append(metrics)

    if not summary:
        print(f"No results found for {dataset_prefix}.")
        return

    df = pd.DataFrame(summary)
    cols = df.columns.tolist()
    header = " | ".join([c.ljust(18) for c in cols])
    print(header)
    print("-" * len(header))
    for _, row in df.iterrows():
        print(" | ".join([str(row[c]).ljust(18) for c in cols]))


if __name__ == "__main__":
    print("\nResults for adult_full:")
    collect_results("adult_full")
