import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def load_and_preprocess(csv_path):
    df = pd.read_csv(csv_path)
    # Average across seeds
    avg_df = df.groupby(["dataset", "synthesizer", "epsilon", "repair_algorithm"]).mean(numeric_only=True).reset_index()
    # Calculate ML Accuracy Delta
    avg_df["ml_acc_delta"] = avg_df["ml_acc_repaired"] - avg_df["ml_acc_synthetic"]
    return avg_df

def plot_deletion_ratio(df, dataset_name):
    ds_df = df[df["dataset"] == dataset_name]
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=ds_df, x="epsilon", y="deletion_ratio", hue="repair_algorithm", style="synthesizer", markers=True)
    plt.title(f"Deletion Ratio vs Epsilon - {dataset_name.capitalize()}")
    plt.ylabel("Deletion Ratio")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

def plot_marginals_error(df, dataset_name):
    ds_df = df[df["dataset"] == dataset_name]
    plt.figure(figsize=(12, 6))
    # Split synthetic trend by synthesizer
    sns.lineplot(data=ds_df, x="epsilon", y="marginals_error_synthetic", hue="synthesizer", palette="Greys", linestyle="--", legend=False)
    sns.lineplot(data=ds_df, x="epsilon", y="marginals_error_repaired", hue="repair_algorithm", style="synthesizer", markers=True)
    plt.title(f"Marginals Error - {dataset_name.capitalize()}")
    plt.ylabel("Avg Marginals Error")
    plt.tight_layout()

def plot_marginals_loss(df, dataset_name):
    ds_df = df[df["dataset"] == dataset_name]
    plt.figure(figsize=(12, 6))
    # Split synthetic trend by synthesizer
    sns.lineplot(data=ds_df, x="epsilon", y="loss_marginal_synthetic", hue="synthesizer", palette="Greys", linestyle="--", legend=False)
    sns.lineplot(data=ds_df, x="epsilon", y="loss_marginal_repaired", hue="repair_algorithm", style="synthesizer", markers=True)
    plt.title(f"Marginals Loss - {dataset_name.capitalize()}")
    plt.ylabel("Marginal Loss Component")
    plt.tight_layout()

def plot_tvd(df, dataset_name):
    ds_df = df[df["dataset"] == dataset_name]
    plt.figure(figsize=(12, 6))
    # Split synthetic trend by synthesizer
    sns.lineplot(data=ds_df, x="epsilon", y="tvd_synthetic", hue="synthesizer", palette="Greys", linestyle="--", legend=False)
    sns.lineplot(data=ds_df, x="epsilon", y="tvd_repaired", hue="repair_algorithm", style="synthesizer", markers=True)
    plt.title(f"TVD (2-way) - {dataset_name.capitalize()}")
    plt.ylabel("Avg TVD")
    plt.tight_layout()

def plot_runtime(df, dataset_name):
    ds_df = df[df["dataset"] == dataset_name]
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=ds_df, x="epsilon", y="runtime", hue="repair_algorithm", style="synthesizer", markers=True)
    plt.title(f"Repair Runtime vs Epsilon - {dataset_name.capitalize()}")
    plt.ylabel("Runtime (s)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

def plot_ml_accuracy(df, dataset_name):
    ds_df = df[df["dataset"] == dataset_name]
    plt.figure(figsize=(12, 6))
    # Split synthetic trend by synthesizer
    sns.lineplot(data=ds_df, x="epsilon", y="ml_acc_synthetic", hue="synthesizer", palette="Greys", linestyle="--", legend=False)
    sns.lineplot(data=ds_df, x="epsilon", y="ml_acc_repaired", hue="repair_algorithm", style="synthesizer", markers=True)
    plt.title(f"ML Accuracy - {dataset_name.capitalize()}")
    plt.ylabel("Avg ML Accuracy")
    plt.tight_layout()
