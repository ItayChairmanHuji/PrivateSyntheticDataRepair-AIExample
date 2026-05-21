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
from shared.entities.pipeline_result import PipelineResult
from s01_loading.src.components.dcs_loader import DCsLoader

@hydra.main(version_base=None, config_path="../config", config_name="default")
def main(cfg: DictConfig):
    print(f"--- Stage 5: Evaluating Results ---")
    
    # Define directories (relative to CWD)
    input_dir = Path("s05_evaluating/input")
    output_dir = Path("s05_evaluating/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load artifacts
    print(f"Loading artifacts from {input_dir}...")
    p_data = pd.read_csv(input_dir / "private_data.csv")
    s_data = pd.read_csv(input_dir / "synthetic_data.csv")
    r_data = pd.read_csv(input_dir / "repaired_data.csv")
    
    with open(input_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
        
    dcs_loader = DCsLoader()
    dcs = dcs_loader.load(input_dir / "constraints.txt")
    
    with open(input_dir / "marginals.json", "r") as f:
        marginals = MarginalSet.from_dict(json.load(f))
        
    p_dataset = Dataset(name=metadata["name"], data=p_data, dcs=dcs, target=metadata["target"])
    s_dataset = Dataset(name=metadata["name"] + "_syn", data=s_data, dcs=dcs, target=metadata["target"])
    r_dataset = Dataset(name=metadata["name"] + "_rep", data=r_data, dcs=dcs, target=metadata["target"])
    
    result = PipelineResult(
        private_dataset=p_dataset,
        synthetic_dataset=s_dataset,
        repaired_dataset=r_dataset,
        obtained_marginals=marginals,
        runtimes={}, # Could be populated if we tracked it
        metadata=metadata
    )
    
    # Instantiate and run orchestrator
    print(f"Instantiating orchestrator...")
    orchestrator = hydra.utils.instantiate(cfg)
    # Ensure output_dir is absolute or relative to project root
    orchestrator.output_dir = str(output_dir)
    
    orchestrator.run(result)
        
    print(f"Success: Evaluation completed.")

if __name__ == "__main__":
    main()
