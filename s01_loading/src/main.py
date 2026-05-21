import hydra
from omegaconf import DictConfig
import os
import sys
import json
from pathlib import Path

# The project root is already in the path when running from root,
# but we ensure it for safety if run from elsewhere.
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

@hydra.main(version_base=None, config_path="../config", config_name="adult100")
def main(cfg: DictConfig):
    print(f"--- Stage 1: Loading Dataset '{cfg.name}' ---")
    
    # Instantiate the loader
    loader = hydra.utils.instantiate(cfg)
    dataset = loader.load()
    
    # Define output directory (relative to CWD)
    output_dir = Path("s01_loading/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving artifacts to {output_dir}...")
    
    # Save artifacts according to Stage 1 Contract
    # 1. private_data.csv
    dataset.data.to_csv(output_dir / "private_data.csv", index=False)
    
    # 2. metadata.json
    # Serialize LabelEncoder mappings
    serializable_mappings = {}
    if dataset.mappings:
        for col, le in dataset.mappings.items():
            serializable_mappings[col] = {str(label): int(idx) for idx, label in enumerate(le.classes_)}

    metadata = {
        "name": dataset.name,
        "target": dataset.target,
        "columns": list(dataset.data.columns),
        "mappings": serializable_mappings
    }
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
        
    # 3. constraints.txt
    with open(output_dir / "constraints.txt", "w") as f:
        f.write(dataset.dcs.to_string())
        
    print(f"Success: Loaded {len(dataset.data)} rows and {len(dataset.dcs.constraints)} constraints.")

if __name__ == "__main__":
    main()
