import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import ast
import numpy as np

# Print confirmation to debug loading issues
# print("Loading visualize_experiment_5.py...")

def safe_parse(val):
    if pd.isna(val):
        return None
    try:
        if isinstance(val, str) and val.strip().startswith('{'):
            return ast.literal_eval(val)
        return val
    except:
        return None

def avg_ml(ml_dict, key):
    if not isinstance(ml_dict, dict) or key not in ml_dict:
        return None
    vals = [v for v in ml_dict[key].values() if v is not None]
    return np.mean(vals) if vals else None

def load_and_preprocess_exp5_data(summary_csv):
    """Loads and cleans Experiment 5 summary results for analysis."""
    if not os.path.exists(summary_csv):
        raise FileNotFoundError(f"Summary CSV not found at: {summary_csv}")
        
    df = pd.read_csv(summary_csv)
    
    # Extract deletion ratio
    df['parsed_dr'] = df['deletion_ratio'].apply(safe_parse)
    df['deletion_ratio_val'] = df['parsed_dr'].apply(lambda x: x.get('ratio') if isinstance(x, dict) else None)
    
    # Extract marginals error
    df['parsed_me'] = df['marginals_error'].apply(safe_parse)
    df['marginals_error_repaired'] = df['parsed_me'].apply(lambda x: x.get('repaired_avg') if isinstance(x, dict) else None)
    df['marginals_error_synthetic'] = df['parsed_me'].apply(lambda x: x.get('synthetic_avg') if isinstance(x, dict) else None)
    
    # Extract TVD (backup for marginals error)
    df['parsed_tvd'] = df['tvd_2way'].apply(safe_parse)
    df['tvd_repaired'] = df['parsed_tvd'].apply(lambda x: x.get('repaired_avg') if isinstance(x, dict) else None)
    df['tvd_synthetic'] = df['parsed_tvd'].apply(lambda x: x.get('synthetic_avg') if isinstance(x, dict) else None)

    # Extract ML accuracy
    df['parsed_ml'] = df['ml_accuracy'].apply(safe_parse)
    df['ml_accuracy_repaired'] = df['parsed_ml'].apply(lambda x: avg_ml(x, 'repaired'))
    df['ml_accuracy_synthetic'] = df['parsed_ml'].apply(lambda x: avg_ml(x, 'synthetic'))

    # Extract Runtimes
    df['parsed_runtime'] = df['runtimes'].apply(safe_parse)
    df['runtime_total'] = df['parsed_runtime'].apply(lambda x: x.get('repair_total') if isinstance(x, dict) else None)

    # Extract Loss components
    df['parsed_loss'] = df['loss_function'].apply(safe_parse)
    df['loss_marginal_repaired'] = df['parsed_loss'].apply(lambda x: x.get('repaired', {}).get('marginal_component') if isinstance(x, dict) else None)
    df['loss_size_repaired'] = df['parsed_loss'].apply(lambda x: x.get('repaired', {}).get('size_component') if isinstance(x, dict) else None)
    
    # Average across seeds
    group_cols = ["dataset", "synthesizer", "epsilon", "repair_algorithm"]
    numeric_cols = [
        "deletion_ratio_val", 
        "ml_accuracy_repaired", "ml_accuracy_synthetic", 
        "marginals_error_repaired", "marginals_error_synthetic",
        "tvd_repaired", "tvd_synthetic",
        "runtime_total", "loss_marginal_repaired", "loss_size_repaired"
    ]
    
    return df.groupby(group_cols)[numeric_cols].mean().reset_index()

def plot_deletion_ratio(avg_df, output_dir=None):
    sns.set_theme(style="whitegrid")
    for ds in avg_df["dataset"].unique():
        plt.figure(figsize=(10, 6))
        ds_df = avg_df[avg_df["dataset"] == ds]
        sns.lineplot(data=ds_df, x="epsilon", y="deletion_ratio_val", hue="repair_algorithm", style="synthesizer", marker="o")
        plt.title(f"Experiment 5: Deletion Ratio - {ds.capitalize()}")
        plt.ylabel("Deletion Ratio")
        plt.xlabel("Epsilon")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        if output_dir:
            plt.savefig(Path(output_dir) / f"exp5_deletion_ratio_{ds}.png")
            plt.close()
        else:
            plt.show()

def plot_ml_accuracy(avg_df, output_dir=None):
    sns.set_theme(style="whitegrid")
    for ds in avg_df["dataset"].unique():
        plt.figure(figsize=(10, 6))
        ds_df = avg_df[avg_df["dataset"] == ds]
        sns.lineplot(data=ds_df, x="epsilon", y="ml_accuracy_repaired", hue="repair_algorithm", style="synthesizer", marker="s")
        sns.lineplot(data=ds_df, x="epsilon", y="ml_accuracy_synthetic", color="black", linestyle="--", alpha=0.5, label="Synthetic (Baseline)")
        plt.title(f"Experiment 5: ML Accuracy - {ds.capitalize()}")
        plt.ylabel("Accuracy")
        plt.xlabel("Epsilon")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        if output_dir:
            plt.savefig(Path(output_dir) / f"exp5_ml_accuracy_{ds}.png")
            plt.close()
        else:
            plt.show()

def plot_data_quality(avg_df, output_dir=None):
    sns.set_theme(style="whitegrid")
    for ds in avg_df["dataset"].unique():
        plt.figure(figsize=(10, 6))
        ds_df = avg_df[avg_df["dataset"] == ds]
        y_col_rep = "marginals_error_repaired"
        y_col_syn = "marginals_error_synthetic"
        metric_name = "Avg Marginals Error"
        if ds_df[y_col_rep].isna().all():
            y_col_rep = "tvd_repaired"
            y_col_syn = "tvd_synthetic"
            metric_name = "Avg 2-Way TVD"
        sns.lineplot(data=ds_df, x="epsilon", y=y_col_rep, hue="repair_algorithm", style="synthesizer", marker="p")
        sns.lineplot(data=ds_df, x="epsilon", y=y_col_syn, color="black", linestyle="--", alpha=0.5, label="Synthetic (Baseline)")
        plt.title(f"Experiment 5: Data Quality ({metric_name}) - {ds.capitalize()}")
        plt.ylabel(metric_name)
        plt.xlabel("Epsilon")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        if output_dir:
            plt.savefig(Path(output_dir) / f"exp5_quality_{ds}.png")
            plt.close()
        else:
            plt.show()

def plot_runtime(avg_df, output_dir=None):
    sns.set_theme(style="whitegrid")
    for ds in avg_df["dataset"].unique():
        plt.figure(figsize=(10, 6))
        ds_df = avg_df[avg_df["dataset"] == ds]
        sns.lineplot(data=ds_df, x="epsilon", y="runtime_total", hue="repair_algorithm", style="synthesizer", marker="x")
        plt.title(f"Experiment 5: Runtime - {ds.capitalize()}")
        plt.ylabel("Seconds")
        plt.xlabel("Epsilon")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        if output_dir:
            plt.savefig(Path(output_dir) / f"exp5_runtime_{ds}.png")
            plt.close()
        else:
            plt.show()

def plot_marginal_loss(avg_df, output_dir=None):
    sns.set_theme(style="whitegrid")
    for ds in avg_df["dataset"].unique():
        plt.figure(figsize=(10, 6))
        ds_df = avg_df[avg_df["dataset"] == ds]
        sns.lineplot(data=ds_df, x="epsilon", y="loss_marginal_repaired", hue="repair_algorithm", style="synthesizer", marker="d")
        plt.title(f"Experiment 5: Marginal Loss - {ds.capitalize()}")
        plt.ylabel("Loss Component")
        plt.xlabel("Epsilon")
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        if output_dir:
            plt.savefig(Path(output_dir) / f"exp5_marginal_loss_{ds}.png")
            plt.close()
        else:
            plt.show()

def plot_experiment_5_trends(summary_csv, output_dir):
    avg_df = load_and_preprocess_exp5_data(summary_csv)
    os.makedirs(output_dir, exist_ok=True)
    
    plot_deletion_ratio(avg_df, output_dir)
    plot_ml_accuracy(avg_df, output_dir)
    plot_data_quality(avg_df, output_dir)
    plot_runtime(avg_df, output_dir)
    plot_marginal_loss(avg_df, output_dir)

    # Summary Stats Table
    summary_table = avg_df.groupby(["dataset", "repair_algorithm"])[["deletion_ratio_val", "ml_accuracy_repaired", "marginals_error_repaired"]].mean().reset_index()
    summary_md = summary_table.to_markdown(index=False)
    with open(Path(output_dir) / "exp5_summary_table.md", "w") as f:
        f.write("# Experiment 5 Summary Results\n\n")
        f.write("Averaged across all epsilons and synthesizers.\n\n")
        f.write(summary_md)

    print(f"Experiment 5 plots and summary table saved to {output_dir}")

if __name__ == "__main__":
    plot_experiment_5_trends(
        summary_csv="remote/output/experiment_5_repair_comparison_summary.csv",
        output_dir="s06_analysis/output/experiment_5_plots"
    )
