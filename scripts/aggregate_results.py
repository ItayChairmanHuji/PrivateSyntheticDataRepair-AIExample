import os
import json
import pandas as pd
from pathlib import Path

def aggregate_results(results_dir="results"):
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
                    
                    # Extract key metrics and parameters
                    row = {
                        "dataset": data.get("dataset_name"),
                        "experiment_name": data.get("experiment_name"),
                        "experiment_id": data.get("experiment_id"),
                        "timestamp": data.get("timestamp")
                    }
                    
                    # Extract runtimes
                    runtimes = data.get("runtimes", {})
                    for k, v in runtimes.items():
                        row[f"runtime_{k}"] = v
                    
                    # Extract metadata (parameters)
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
                    
                    # Extract evaluation metrics
                    # Note: We flatten the metrics structure
                    for k, v in data.items():
                        if k in ["dataset_name", "experiment_name", "experiment_id", "timestamp", "runtimes", "metadata"]:
                            continue
                        
                        if isinstance(v, dict):
                            for sub_k, sub_v in v.items():
                                if not isinstance(sub_v, (dict, list)):
                                    row[f"{k}_{sub_k}"] = sub_v
                        elif not isinstance(v, (dict, list)):
                            row[k] = v
                            
                    all_data.append(row)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    if not all_data:
        print("No valid result files found.")
        return

    df = pd.DataFrame(all_data)
    
    # Save to CSV
    output_file = "experiment_results_summary.csv"
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
    args = parser.parse_args()
    
    aggregate_results(args.dir)
