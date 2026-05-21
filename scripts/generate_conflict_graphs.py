import hydra
from omegaconf import DictConfig
from src.entities.dataset import Dataset
import igraph as ig
import os
from pathlib import Path
import pandas as pd

@hydra.main(config_path="../config", config_name="config", version_base=None)
def main(cfg: DictConfig):
    # 1. Load dataset (primarily for DCs and metadata)
    # We use the loader defined in config (e.g., loading=adult)
    print(f"Loading dataset using config: {cfg.loading._target_}")
    loader = hydra.utils.instantiate(cfg.loading)
    dataset = loader.load()
    
    # 2. Instantiate synthesizer (expected to be model_loader)
    print(f"Instantiating synthesizer: {cfg.synthesizing._target_}")
    synthesizer = hydra.utils.instantiate(cfg.synthesizing)
    
    # 3. Generate synthetic data
    print("Generating synthetic data...")
    synth_dataset = synthesizer.synthesize(dataset)
    
    # 4. Get violations
    print("Finding violations...")
    violations = synth_dataset.get_violations()
    print(f"Found {len(violations)} violations.")
    
    # 5. Build conflict graph
    print("Building conflict graph...")
    n = len(synth_dataset.data)
    graph = ig.Graph(n)
    graph.vs["original_index"] = list(range(n))
    
    if not violations.empty:
        # Ensure indices are integers
        idx1 = violations['idx1'].values.astype(int)
        idx2 = violations['idx2'].values.astype(int)
        edges = list(zip(idx1, idx2))
        graph.add_edges(edges)
        graph.simplify()
    
    # 6. Save graph
    output_dir = Path("outputs/graphs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Construct filename
    # Try to extract model info from config
    model_path_str = getattr(cfg.synthesizing, "model_path", "unknown_model")
    model_name = Path(model_path_str).stem
    
    # Use the experiment_name if provided, otherwise use dataset and model name
    exp_name = getattr(cfg, "experiment_name", f"{dataset.name}_{model_name}")
    
    filename = f"{exp_name}_graph.graphml"
    save_path = output_dir / filename
    
    print(f"Saving graph to {save_path}...")
    graph.write_graphml(str(save_path))
    print("Done.")

if __name__ == "__main__":
    main()
