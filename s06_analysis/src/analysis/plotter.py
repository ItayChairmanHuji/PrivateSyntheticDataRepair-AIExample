import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from dataclasses import dataclass
import numpy as np

@dataclass
class AnalysisPlotter:
    """Standardized plotting functions for research analysis."""
    output_dir: Path = Path("plots")
    style: str = "whitegrid"

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style=self.style)
        plt.rcParams.update({
            'axes.titlesize': 22,
            'axes.labelsize': 18,
            'xtick.labelsize': 14,
            'ytick.labelsize': 14,
            'legend.fontsize': 16,
            'figure.titlesize': 26
        })

    def _save_and_show(self, filename: str):
        plt.tight_layout()
        plt.savefig(self.output_dir / filename, dpi=300)
        plt.show()
        plt.close('all')

    def plot_repair_trends(self, df: pd.DataFrame):
        """
        Plots deletion ratio and averaged ML accuracy.
        ONE GRAPH PER PLOT.
        """
        for ds in df['dataset'].unique():
            ds_df = df[df['dataset'] == ds]
            avg_df = ds_df.groupby(["synthesizer", "epsilon", "repair_algorithm"])[
                ["deletion_ratio", "ml_acc_repaired", "ml_acc_synthetic"]
            ].mean().reset_index()
            
            # 1. Deletion Ratio
            plt.figure(figsize=(16, 10))
            sns.lineplot(data=avg_df, x="epsilon", y="deletion_ratio", 
                         hue="repair_algorithm", style="synthesizer", markers=True, linewidth=3)
            plt.title(f"Deletion Ratio: {ds.capitalize()}")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            self._save_and_show(f"deletion_ratio_{ds}.png")

            # 2. Averaged ML Accuracy
            plt.figure(figsize=(16, 10))
            sns.lineplot(data=avg_df, x="epsilon", y="ml_acc_repaired", 
                         hue="repair_algorithm", style="synthesizer", markers=True, linewidth=3)
            # Add synthetic baselines
            for synth in avg_df['synthesizer'].unique():
                synth_val = avg_df[avg_df['synthesizer'] == synth]['ml_acc_synthetic'].mean()
                plt.axhline(y=synth_val, color='gray', linestyle='--', alpha=0.5, label=f"Synthetic ({synth})")
            
            plt.title(f"ML Accuracy (Averaged): {ds.capitalize()}")
            plt.ylabel("Accuracy")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            self._save_and_show(f"ml_accuracy_avg_{ds}.png")

    def plot_detailed_ml_accuracy(self, df: pd.DataFrame):
        """Plots ML accuracy for each model type (LR, RF, MLP) individually."""
        models = ['logistic_regression', 'random_forest', 'mlp']
        for ds in df['dataset'].unique():
            ds_df = df[df['dataset'] == ds]
            for model in models:
                y_col, y_syn = f'ml_acc_{model}_repaired', f'ml_acc_{model}_synthetic'
                if y_col not in ds_df.columns: continue
                
                avg_df = ds_df.groupby(["synthesizer", "epsilon", "repair_algorithm"])[[y_col, y_syn]].mean().reset_index()
                
                plt.figure(figsize=(16, 10))
                sns.lineplot(data=avg_df, x="epsilon", y=y_col, 
                             hue="repair_algorithm", style="synthesizer", markers=True, linewidth=3)
                
                # Baseline
                for synth in avg_df['synthesizer'].unique():
                    val = avg_df[avg_df['synthesizer'] == synth][y_syn].mean()
                    plt.axhline(y=val, color='gray', linestyle='--', alpha=0.4, label=f"Baseline ({synth})")
                
                plt.title(f"ML Accuracy - {model.replace('_', ' ').capitalize()}: {ds.capitalize()}")
                plt.ylabel("Accuracy")
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                self._save_and_show(f"ml_accuracy_{model}_{ds}.png")

    def plot_quality_trends(self, df: pd.DataFrame):
        """Plots marginals error, TVD, and loss component individually."""
        metrics = [
            ('marginals_error_repaired', 'Marginals Error'), 
            ('tvd_repaired', '2-Way TVD'), 
            ('loss_marginal_repaired', 'Marginal Loss Component')
        ]
        for ds in df['dataset'].unique():
            ds_df = df[df['dataset'] == ds]
            for col, label in metrics:
                if col not in ds_df.columns: continue
                avg_df = ds_df.groupby(["synthesizer", "epsilon", "repair_algorithm"])[col].mean().reset_index()
                
                plt.figure(figsize=(16, 10))
                sns.lineplot(data=avg_df, x="epsilon", y=col, 
                             hue="repair_algorithm", style="synthesizer", markers=True, linewidth=3)
                plt.title(f"{label}: {ds.capitalize()}")
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                self._save_and_show(f"quality_{col}_{ds}.png")

    def plot_utility_error_tradeoff(self, df: pd.DataFrame):
        """Plots the tradeoff between marginals error and ML accuracy."""
        for ds in df['dataset'].unique():
            ds_df = df[df['dataset'] == ds]
            syn_df, rep_df = ds_df.copy(), ds_df.copy()
            syn_df["Algorithm"], rep_df["Algorithm"] = "Synthetic", rep_df["repair_algorithm"]
            syn_df = syn_df.rename(columns={"marginals_error_synthetic": "error", "ml_acc_synthetic": "accuracy"})
            rep_df = rep_df.rename(columns={"marginals_error_repaired": "error", "ml_acc_repaired": "accuracy"})
            plot_df = pd.concat([syn_df, rep_df]).groupby(["synthesizer", "epsilon", "Algorithm"])[["error", "accuracy"]].mean().reset_index()
            
            plt.figure(figsize=(16, 12))
            sns.scatterplot(data=plot_df, x="error", y="accuracy", hue="Algorithm", style="synthesizer", s=300)
            plt.title(f"Utility-Consistency Tradeoff: {ds.capitalize()}")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.grid(True, linestyle='--', alpha=0.6)
            self._save_and_show(f"utility_error_tradeoff_{ds}.png")

    def plot_adaptive_metrics(self, df: pd.DataFrame):
        """Plots alpha, hubbiness, and connectivity vs Epsilon for Weighted VC."""
        weighted_df = df[df["repair_algorithm"] == "weighted_vc"]
        if weighted_df.empty: return
        metrics = ["mean_alpha", "mean_hubbiness", "mean_connectivity"]
        avg_df = weighted_df.groupby(["dataset", "synthesizer", "epsilon"])[metrics].mean().reset_index()
        for ds in avg_df['dataset'].unique():
            ds_df = avg_df[avg_df['dataset'] == ds]
            melted = ds_df.melt(id_vars=["epsilon", "synthesizer"], value_vars=metrics, var_name="metric", value_name="value")
            melted["metric"] = melted["metric"].str.replace("mean_", "")
            
            plt.figure(figsize=(16, 10))
            sns.lineplot(data=melted, x="epsilon", y="value", hue="metric", style="synthesizer", markers=True, linewidth=4)
            plt.title(f"Adaptive Graph Metrics vs Epsilon: {ds.capitalize()}")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            self._save_and_show(f"adaptive_metrics_epsilon_{ds}.png")

    def plot_iteration_topology(self, df_topo: pd.DataFrame):
        """Plots graph topology evolution across repair iterations."""
        if df_topo.empty: return
        for ds in df_topo['dataset'].unique():
            ds_topo = df_topo[df_topo['dataset'] == ds]
            avg_topo = ds_topo.groupby(["epsilon", "synthesizer", "iteration"])[["alpha", "hubbiness", "connectivity"]].mean().reset_index()
            epsilons = sorted(avg_topo['epsilon'].unique())
            selected_eps = [epsilons[0], epsilons[len(epsilons)//2], epsilons[-1]] if len(epsilons) > 3 else epsilons
            for eps in selected_eps:
                eps_df = avg_topo[avg_topo['epsilon'] == eps]
                melted = eps_df.melt(id_vars=["iteration", "synthesizer"], value_vars=["alpha", "hubbiness", "connectivity"], var_name="metric", value_name="value")
                
                plt.figure(figsize=(18, 10))
                sns.lineplot(data=melted, x="iteration", y="value", hue="metric", style="synthesizer", linewidth=3)
                plt.title(f"Graph Evolution: {ds.capitalize()} (eps={eps})")
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                self._save_and_show(f"graph_evolution_{ds}_eps{eps}.png")

    def plot_runtime(self, df: pd.DataFrame):
        """Plots repair runtime comparison."""
        for ds in df['dataset'].unique():
            ds_df = df[df['dataset'] == ds]
            avg_df = ds_df.groupby(["epsilon", "repair_algorithm", "synthesizer"])["repair_runtime"].mean().reset_index()
            plt.figure(figsize=(16, 10))
            sns.lineplot(data=avg_df, x="epsilon", y="repair_runtime", hue="repair_algorithm", style="synthesizer", marker="d", linewidth=3)
            plt.title(f"Repair Runtime: {ds.capitalize()}")
            plt.ylabel("Seconds")
            self._save_and_show(f"runtime_{ds}.png")

    def generate_summary_table(self, df: pd.DataFrame):
        """Generates a markdown summary table."""
        metrics = ["deletion_ratio", "ml_acc_repaired", "marginals_error_repaired", "mean_alpha"]
        metrics = [m for m in metrics if m in df.columns]
        summary = df.groupby(["dataset", "repair_algorithm"])[metrics].mean().reset_index()
        md_table = summary.to_markdown(index=False)
        with open(self.output_dir.parent / "summary_table.md", "w") as f:
            f.write(md_table)
        print(md_table)
