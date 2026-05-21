import hydra
from omegaconf import DictConfig
import os
import sys
import pandas as pd
import json
from pathlib import Path

# Root in path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from shared.entities.dataset import Dataset
from shared.utils.mbi_patch import apply_patch
from s01_loading.src.components.dcs_loader import DCsLoader

# Apply reproducibility patch for mbi
apply_patch()

@hydra.main(version_base=None, config_path="../config", config_name="mst")
def main(cfg: DictConfig):
    print(f"--- Stage 2: Synthesizing Dataset ---")
    
    # Define directories
    input_dir = Path(__file__).resolve().parent.parent / "input"
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 1. Load artifacts from Stage 1
    print(f"Loading artifacts from {input_dir}...")
    data = pd.read_csv(input_dir / "private_data.csv")
    
    with open(input_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
        
    dcs_loader = DCsLoader()
    dcs = dcs_loader.load(input_dir / "constraints.txt")
    
    # 2. Reconstruct Dataset object
    dataset = Dataset(
        name=metadata["name"],
        data=data,
        dcs=dcs,
        target=metadata["target"]
    )
    
    # 3. Instantiate and run synthesizer
    print(f"Instantiating synthesizer: {cfg._target_}")
    synthesizer = hydra.utils.instantiate(cfg)
    
    print(f"Running synthesis (engine={cfg.engine}, epsilon={cfg.epsilon})...")
    synthetic_dataset = synthesizer.synthesize(dataset)
    
    # 4. Save artifacts
    print(f"Saving synthetic data to {output_dir}...")
    synthetic_dataset.data.to_csv(output_dir / "synthetic_data.csv", index=False)
    
    # Save run config for interpretability (Glass Box)
    run_config = {
        "synthesizer": cfg.engine,
        "epsilon": cfg.epsilon,
        "seed": cfg.seed,
        "size": len(synthetic_dataset.data)
    }
    with open(output_dir / "run_config.json", "w") as f:
        json.dump(run_config, f, indent=4)
        
    print(f"Success: Generated {len(synthetic_dataset.data)} synthetic rows.")

if __name__ == "__main__":
    main()
