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
    print(f"--- Stage 4: Repairing Synthetic Data ---")
    
    # Define directories (relative to CWD)
    input_dir = Path("s04_repairing/input")
    output_dir = Path("s04_repairing/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load artifacts
    print(f"Loading artifacts from {input_dir}...")
    s_data = pd.read_csv(input_dir / "synthetic_data.csv")
    
    with open(input_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
        
    dcs_loader = DCsLoader()
    dcs = dcs_loader.load(input_dir / "constraints.txt")
    
    with open(input_dir / "marginals.json", "r") as f:
        marginals = MarginalSet.from_dict(json.load(f))
        
    s_dataset = Dataset(name=metadata["name"] + "_syn", data=s_data, dcs=dcs, target=metadata["target"])
    
    # Instantiate and run repairer
    print(f"Instantiating repairer: {cfg._target_}")
    repairer = hydra.utils.instantiate(cfg)
    repaired_dataset = repairer.repair(s_dataset, marginals)
    
    # Save artifacts
    print(f"Saving repaired data to {output_dir}...")
    repaired_dataset.data.to_csv(output_dir / "repaired_data.csv", index=False)
        
    print(f"Success: Repaired dataset saved.")

if __name__ == "__main__":
    main()
