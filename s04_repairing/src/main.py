import hydra
from omegaconf import DictConfig
import os
import sys
import pandas as pd
import json
from pathlib import Path

# Root in path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s01_loading.src.components.dcs_loader import DCsLoader

@hydra.main(version_base=None, config_path="../config", config_name="vanilla_vc")
def main(cfg: DictConfig):
    dataset_name = cfg.get("dataset_name")
    if not dataset_name:
        print("Error: dataset_name must be provided in config or as an argument (e.g., dataset_name=adult100)")
        return

    print(f"--- Stage 4: Repairing Synthetic Data [{dataset_name}] ---")
    
    # Define directories (relative to CWD)
    input_dir = Path("s04_repairing/input") / dataset_name
    output_dir = Path("s04_repairing/output") / dataset_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load artifacts
    print(f"Loading artifacts from {input_dir}...")
    if not (input_dir / "synthetic_data.csv").exists():
        print(f"Error: Required artifact 'synthetic_data.csv' not found in {input_dir}")
        return
        
    s_data = pd.read_csv(input_dir / "synthetic_data.csv")
    
    with open(input_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
        
    dcs_loader = DCsLoader()
    dcs = dcs_loader.load(input_dir / "constraints.txt")
    
    # Load marginals
    marginals_path = input_dir / "marginals.json"
    if not marginals_path.exists():
        print(f"Error: Required artifact 'marginals.json' not found in {input_dir}")
        return

    with open(marginals_path, "r") as f:
        marginals = MarginalSet.from_dict(json.load(f))
        
    s_dataset = Dataset(name=metadata["name"] + "_syn", data=s_data, dcs=dcs, target=metadata["target"])
    
    # Instantiate and run repairer
    print(f"Instantiating repairer: {cfg._target_}")
    repairer = hydra.utils.instantiate(cfg)
    repaired_dataset = repairer.repair(s_dataset, marginals)
    
    # Save artifacts
    print(f"Saving repaired data to {output_dir}...")
    repaired_dataset.data.to_csv(output_dir / "repaired_data.csv", index=False)
        
    print(f"Success: Repaired dataset saved to {output_dir / 'repaired_data.csv'}")

if __name__ == "__main__":
    main()
