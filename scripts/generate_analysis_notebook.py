
import os
import json
import pandas as pd
from pathlib import Path

def generate_analysis_notebook(results_dir="results/full_repair_grid", output_path="notebooks/final_experiment_analysis.ipynb"):
    # 1. Aggregate results
    all_data = []
    results_path = Path(results_dir)
    
    for root, _, files in os.walk(results_dir):
        for file in files:
            if file.endswith(".json") and file.startswith("result_"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    
                    if data.get("experiment_name") != "full_repair_grid":
                        continue
                        
                    metadata = data.get("metadata", {})
                    rep_params = metadata.get("repairer_params", {})
                    synth_params = metadata.get("synthesizer_params", {})
                    
                    engine = synth_params.get("engine")
                    if not engine and "model_path" in synth_params:
                        model_path = synth_params["model_path"]
                        if "mst" in model_path.lower(): engine = "mst"
                        elif "aim" in model_path.lower(): engine = "aim"
                        elif "patectgan" in model_path.lower(): engine = "patectgan"
                    
                    repairer = metadata.get("repairer")
                    if repairer == "ILPRepairer":
                        use_marg = rep_params.get("use_marginals")
                        repairer = f"ILP (marginals={use_marg})"
                    
                    row = {
                        "dataset": data.get("dataset_name"),
                        "engine": engine,
                        "repairer": repairer,
                        "deletion_ratio": data.get("deletion_ratio", {}).get("ratio"),
                        "tvd": data.get("tvd_2way", {}).get("repaired_avg"),
                        "marginal_error": data.get("marginals_error", {}).get("repaired_avg"),
                        "runtime": data.get("runtimes", {}).get("repairing")
                    }
                    all_data.append(row)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

    df = pd.DataFrame(all_data)
    df.to_csv("results/aggregated_final_results.csv", index=False)
    
    # 2. Construct raw notebook JSON
    cells = []
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# Final Experiment Analysis\n", "Analysis of deletion ratio, TVD, marginal error, and runtime across all datasets and algorithms."]
    })
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import pandas as pd\n",
            "import numpy as np\n",
            "\n",
            "# Load aggregated data\n",
            "df = pd.read_csv('../results/aggregated_final_results.csv')\n",
            "\n",
            "# Define metrics to analyze\n",
            "metrics = {\n",
            "    'deletion_ratio': 'Deletion Ratio',\n",
            "    'tvd': 'Total Variation Distance (TVD)',\n",
            "    'marginal_error': 'Marginal Error',\n",
            "    'runtime': 'Repair Runtime (seconds)'\n",
            "}"
        ]
    })
    
    # Define metrics to analyze
    metrics = {
        'deletion_ratio': 'Deletion Ratio',
        'tvd': 'Total Variation Distance (TVD)',
        'marginal_error': 'Marginal Error',
        'runtime': 'Repair Runtime (seconds)'
    }
    
    datasets = sorted(df['dataset'].unique())
    for dataset in datasets:
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"## Dataset: {dataset.upper()}"]
        })
        
        for metric_key, metric_name in metrics.items():
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"### Metric: {metric_name}"]
            })
            
            code = [
                f"ds_df = df[df['dataset'] == '{dataset}']\n",
                f"pivot_table = ds_df.groupby(['repairer', 'engine'])['{metric_key}'].mean().unstack()\n",
                "\n",
                "cols = ['mst', 'aim', 'patectgan']\n",
                "pivot_table = pivot_table.reindex(columns=[c for c in cols if c in pivot_table.columns])\n",
                "\n",
                f"print(f'Dataset: {dataset} | Metric: {metric_name}')\n",
                "pivot_table"
            ]
            cells.append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code
            })

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.10.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(output_path, 'w') as f:
        json.dump(nb, f, indent=1)
    
    print(f"Notebook generated: {output_path}")

if __name__ == "__main__":
    generate_analysis_notebook()
