import os, sys, numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
from dataclasses import dataclass
sys.path.append(os.getcwd())
from src.loading.file_loader import FileLoader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder
from src.synthesizing.model_loader import SmartNoiseModelLoader
from src.marginals_obtaining.top_k_obtainer import TopKObtainer
from src.marginals_obtaining.utility_functions.distance_utility import DistanceUtility
from src.repairing.weighted_vc_repairer import WeightedVCRepairer
from src.utils.mbi_patch import apply_patch

@dataclass
class StatWeightedVCRepairer(WeightedVCRepairer):
    def __init__(self, alpha, output_dir, max_plots=50):
        super().__init__(alpha=alpha)
        self.output_dir, self.iteration, self.max_plots = output_dir, 0, max_plots
        os.makedirs(output_dir, exist_ok=True)
    
    def _pick_best_vertex(self, active_indices, weights, graph):
        degrees = np.array([graph.degree(v_idx) for v_idx in active_indices])
        nw, nd = self._normalize(weights), self._normalize(degrees)
        ratios = (1-self.alpha)*np.log(nw) - self.alpha*np.log(nd)
        
        # Limit plotting to avoid thousands of files
        if self.iteration < self.max_plots:
            self._plot_joint_stats(nw, nd, ratios)
        elif self.iteration % 100 == 0:
             print(f"Iteration {self.iteration}...")
        
        self.iteration += 1
        return super()._pick_best_vertex(active_indices, weights, graph)
    
    def _plot_joint_stats(self, nw, nd, scores):
        best_idx = np.argmin(scores)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        ax = axes[0, 0]
        # Use hexbin for 50k rows to handle density
        if len(nw) > 5000:
            scatter = ax.hexbin(nw, nd, C=scores, gridsize=30, cmap='viridis_r', reduce_C_function=np.min)
            fig.colorbar(scatter, ax=ax, label='Min Score in Bin')
        else:
            scatter = ax.scatter(nw, nd, c=scores, cmap='viridis_r', alpha=0.5, edgecolors='none', s=20)
            fig.colorbar(scatter, ax=ax, label='Score')
            
        ax.scatter(nw[best_idx], nd[best_idx], color='red', marker='*', s=200, label='Selected', edgecolors='black')
        ax.set_title(f'Iteration {self.iteration}: Weight vs Degree')
        ax.set_xlabel('Normed Weight')
        ax.set_ylabel('Normed Degree')
        ax.legend()
        
        sns.histplot(nw, ax=axes[0, 1], kde=True, color='blue')
        axes[0, 1].set_title('Weight Dist')
        sns.histplot(nd, ax=axes[1, 0], kde=True, color='green')
        axes[1, 0].set_title('Degree Dist')
        sns.histplot(scores, ax=axes[1, 1], kde=True, color='red')
        axes[1, 1].set_title('Score Dist')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'joint_{self.iteration:04d}.png'))
        plt.close()

def run_exp(d, m, size):
    path = f"models/{d}_{m}.pkl"
    if not os.path.exists(path): return
    print(f"\n>>> Running {d}-{m} at size {size}")
    ds = FileLoader(d, "data", DataLoader(), DCsLoader(), MetadataLoader(), DataEncoder(), DCsEncoder()).load()
    sds = SmartNoiseModelLoader(path, size=size).synthesize(ds)
    margs = TopKObtainer(1.0, 1.0, 10, DistanceUtility()).obtain(ds, sds)
    out = f"outputs/joint_{d}_{m}_{size}"
    repairer = StatWeightedVCRepairer(0.5, out, 50)
    repairer.repair(sds, margs)
    print(f"Done. Total iterations: {repairer.iteration}. Results in {out}")

if __name__ == "__main__":
    apply_patch()
    run_exp("adult", "aim", 50000)
