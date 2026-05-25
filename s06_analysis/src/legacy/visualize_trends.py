import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

def plot_experiment_2_trends(summary_csv, output_dir):
    df = pd.read_csv(summary_csv)
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter for a single seed to show clean trends, or average across seeds
    # Let's average across seeds
    avg_df = df.groupby(["dataset", "synthesizer", "epsilon", "repair_algorithm"]).mean(numeric_only=True).reset_index()
    
    # 1. Violations vs Epsilon
    plt.figure(figsize=(12, 8))
    sns.lineplot(data=avg_df, x="epsilon", y="violations_synthetic", hue="dataset", style="synthesizer", marker="o")
    plt.yscale("log")
    plt.title("Synthetic Violations (Pre-Repair) vs Epsilon")
    plt.ylabel("Violation Count (Log Scale)")
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.savefig(Path(output_dir) / "violations_pre_repair.png")
    plt.close()
    
    # 2. Deletion Ratio vs Epsilon
    plt.figure(figsize=(12, 8))
    sns.lineplot(data=avg_df, x="epsilon", y="deletion_ratio", hue="repair_algorithm", style="dataset", marker="o")
    plt.title("Repair Deletion Ratio vs Epsilon")
    plt.ylabel("Deletion Ratio")
    plt.grid(True, alpha=0.3)
    plt.savefig(Path(output_dir) / "deletion_ratio_vs_epsilon.png")
    plt.close()
    
    # 3. ML Accuracy vs Epsilon (Repaired vs Synthetic)
    for ds in avg_df["dataset"].unique():
        plt.figure(figsize=(10, 6))
        ds_df = avg_df[avg_df["dataset"] == ds]
        sns.lineplot(data=ds_df, x="epsilon", y="ml_acc_synthetic", label="Synthetic (Pre-Repair)", color="black", linestyle="--", marker="x")
        sns.lineplot(data=ds_df, x="epsilon", y="ml_acc_repaired", hue="repair_algorithm", marker="o")
        plt.title(f"ML Accuracy vs Epsilon - {ds.capitalize()}")
        plt.ylabel("Avg ML Accuracy (LR, RF, MLP)")
        plt.grid(True, alpha=0.3)
        plt.savefig(Path(output_dir) / f"ml_acc_{ds}_vs_epsilon.png")
        plt.close()

    print(f"Plots saved to {output_dir}")

if __name__ == "__main__":
    plot_experiment_2_trends(
        summary_csv="s06_analysis/output/experiment_2_summary.csv",
        output_dir="s06_analysis/output/plots"
    )
