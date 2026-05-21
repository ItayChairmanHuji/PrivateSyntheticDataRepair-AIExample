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
    mode = cfg.get("mode", "full")
    print(f"--- Stage 2: Synthesizing Dataset (Mode: {mode}) ---")
    
    # Define directories (relative to CWD)
    input_dir = Path("s02_synthesizing/input")
    output_dir = Path("s02_synthesizing/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    if mode == "train":
        print(f"Running training only (engine={cfg.engine}, epsilon={cfg.epsilon})...")
        # If the synthesizer is a model trainer, it will save the model during synthesize()
        # but we might want to ensure it doesn't sample if we really want "no sample"
        # For now, we'll assume synthesize() handles training and saving.
        # We'll modify the trainer to respect the mode if possible, or just call fit.
        if hasattr(synthesizer, 'fit_and_save'): # We'll add this method
             synthesizer.fit_and_save(dataset)
        else:
             # Fallback: run full but we won't use the sample
             synthesizer.synthesize(dataset)
        print(f"Success: Model trained and saved.")
    else:
        print(f"Running full synthesis (engine={cfg.engine}, epsilon={cfg.epsilon})...")
        synthetic_dataset = synthesizer.synthesize(dataset)
        
        # 4. Save artifacts
        print(f"Saving synthetic data to {output_dir}...")
        synthetic_dataset.data.to_csv(output_dir / "synthetic_data.csv", index=False)
        
        # Save run config for interpretability
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
