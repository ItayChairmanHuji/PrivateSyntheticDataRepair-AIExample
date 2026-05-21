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
from s01_loading.src.components.dcs_loader import DCsLoader

@hydra.main(version_base=None, config_path="../config", config_name="top_k")
def main(cfg: DictConfig):
    print(f"--- Stage 3: Obtaining Marginals ---")
    
    # Define directories (relative to CWD)
    input_dir = Path("s03_marginals/input")
    output_dir = Path("s03_marginals/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load artifacts
    print(f"Loading artifacts from {input_dir}...")
    p_data = pd.read_csv(input_dir / "private_data.csv")
    s_data = pd.read_csv(input_dir / "synthetic_data.csv")
    
    with open(input_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
        
    dcs_loader = DCsLoader()
    dcs = dcs_loader.load(input_dir / "constraints.txt")
    
    p_dataset = Dataset(name=metadata["name"], data=p_data, dcs=dcs, target=metadata["target"])
    s_dataset = Dataset(name=metadata["name"] + "_syn", data=s_data, dcs=dcs, target=metadata["target"])
    
    # Instantiate and run obtainer
    print(f"Instantiating obtainer: {cfg._target_}")
    obtainer = hydra.utils.instantiate(cfg)
    marginals = obtainer.obtain(p_dataset, s_dataset)
    
    # Save artifacts
    print(f"Saving {len(marginals.marginals)} marginals to {output_dir}...")
    with open(output_dir / "marginals.json", "w") as f:
        json.dump(marginals.to_dict(), f, indent=4)
        
    print(f"Success: Obtained {len(marginals.marginals)} marginals.")

if __name__ == "__main__":
    main()
