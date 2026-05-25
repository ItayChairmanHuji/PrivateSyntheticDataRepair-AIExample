import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

def plot_experiment_4_trends(summary_csv, output_dir):
    df = pd.read_csv(summary_csv)
    os.makedirs(output_dir, exist_ok=True)
    
    # Average across seeds
    avg_df = df.groupby(["dataset", "synthesizer", "epsilon", "repair_algorithm"]).mean(numeric_only=True).reset_index()
    
    # Set the style
    sns.set_theme(style="whitegrid")
    
    # 1. Deletion Ratio comparison
    plt.figure(figsize=(14, 8))
    sns.lineplot(data=avg_df, x="epsilon", y="deletion_ratio", hue="repair_algorithm", style="dataset", marker="o")
    plt.title("Experiment 4: Repair Deletion Ratio comparison")
    plt.ylabel("Deletion Ratio")
    plt.xlabel("Epsilon")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "exp4_deletion_ratio.png")
    plt.close()
    
    # 2. ML Accuracy Delta (Repaired - Synthetic)
    avg_df["ml_acc_delta"] = avg_df["ml_acc_repaired"] - avg_df["ml_acc_synthetic"]
    plt.figure(figsize=(14, 8))
    sns.lineplot(data=avg_df, x="epsilon", y="ml_acc_delta", hue="repair_algorithm", style="dataset", marker="s")
    plt.axhline(0, color='black', linestyle='--')
    plt.title("Experiment 4: ML Accuracy Change (Repaired - Synthetic)")
    plt.ylabel("ML Accuracy Delta")
    plt.xlabel("Epsilon")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "exp4_ml_accuracy_delta.png")
    plt.close()

    # 3. Marginals Error (Synthetic vs Repaired)
    for ds in avg_df["dataset"].unique():
        plt.figure(figsize=(12, 6))
        ds_df = avg_df[avg_df["dataset"] == ds]
        sns.lineplot(data=ds_df, x="epsilon", y="marginals_error_synthetic", label="Synthetic (Pre-Repair)", color="black", linestyle="--", marker="x")
        sns.lineplot(data=ds_df, x="epsilon", y="marginals_error_repaired", hue="repair_algorithm", marker="o")
        plt.title(f"Experiment 4: Marginals Error - {ds.capitalize()}")
        plt.ylabel("Avg Marginals Error")
        plt.xlabel("Epsilon")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(Path(output_dir) / f"exp4_marginals_error_{ds}.png")
        plt.close()

    # 4. Summary Table (Markdown)
    summary_table = avg_df.groupby(["dataset", "repair_algorithm"])[["deletion_ratio", "ml_acc_repaired", "marginals_error_repaired"]].mean().reset_index()
    summary_md = summary_table.to_markdown(index=False)
    with open(Path(output_dir) / "exp4_summary_table.md", "w") as f:
        f.write("# Experiment 4 Summary Results\n\n")
        f.write(summary_md)

    print(f"Plots and summary table saved to {output_dir}")

if __name__ == "__main__":
    plot_experiment_4_trends(
        summary_csv="s06_analysis/output/experiment_4_summary.csv",
        output_dir="s06_analysis/output/experiment_4_plots"
    )
