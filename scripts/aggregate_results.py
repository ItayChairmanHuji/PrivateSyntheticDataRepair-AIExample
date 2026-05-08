import os
import json
import pandas as pd
from pathlib import Path

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def aggregate_results(results_dir="results", output_file="experiment_results_summary.csv"):
    all_data = []
    
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"Results directory {results_dir} not found.")
        return

    # Walk through all subdirectories in results/
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file.endswith(".json") and file.startswith("result_"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    
                    # Extract key info
                    row = {
                        "dataset": data.get("dataset_name"),
                        "experiment_name": data.get("experiment_name"),
                        "experiment_id": data.get("experiment_id"),
                        "timestamp": data.get("timestamp")
                    }
                    
                    # Metadata extraction (parameters)
                    metadata = data.get("metadata", {})
                    row["repairer"] = metadata.get("repairer")
                    row["synthesizer"] = metadata.get("synthesizer")
                    
                    synth_params = metadata.get("synthesizer_params", {})
                    engine = synth_params.get("engine")
                    if not engine and "model_path" in synth_params:
                        model_path = synth_params["model_path"]
                        if "mst" in model_path.lower():
                            engine = "mst"
                        elif "aim" in model_path.lower():
                            engine = "aim"
                        elif "patectgan" in model_path.lower():
                            engine = "patectgan"
                    
                    row["engine"] = engine
                    row["iters"] = synth_params.get("num_of_iterations")
                    row["seed"] = synth_params.get("seed")
                    
                    obt_params = metadata.get("obtainer_params", {})
                    row["k"] = obt_params.get("k")
                    row["sel_budget"] = obt_params.get("selection_budget")
                    row["gen_budget"] = obt_params.get("generation_budget")
                    
                    rep_params = metadata.get("repairer_params", {})
                    row["alpha"] = rep_params.get("alpha")
                    row["use_marginals"] = rep_params.get("use_marginals")
                    
                    # Flatten the rest of the metrics
                    metrics = {k: v for k, v in data.items() if k not in ["dataset_name", "experiment_name", "experiment_id", "timestamp", "metadata"]}
                    flattened_metrics = flatten_dict(metrics)
                    
                    # Fix runtime keys to match expected runtime_repairing etc if needed
                    for k, v in flattened_metrics.items():
                        if k.startswith("runtimes_"):
                            row[k.replace("runtimes_", "runtime_")] = v
                        else:
                            row[k] = v
                            
                    all_data.append(row)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    if not all_data:
        print("No valid result files found.")
        return

    df = pd.DataFrame(all_data)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Aggregated {len(all_data)} results into {output_file}")
    
    # Basic summary stats
    print("\nSummary by Algorithm:")
    if "repairer" in df.columns:
        print(df.groupby("repairer").size())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Aggregate all JSON results into a single CSV.")
    parser.add_argument("--dir", type=str, default="results", help="Directory containing results")
    parser.add_argument("--output", type=str, default="experiment_results_summary.csv", help="Output CSV file")
    args = parser.parse_args()
    
    aggregate_results(args.dir, args.output)
