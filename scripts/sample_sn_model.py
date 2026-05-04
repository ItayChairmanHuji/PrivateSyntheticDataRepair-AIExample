import os
import dill
import hydra
from omegaconf import DictConfig
import pandas as pd
from pathlib import Path

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

@hydra.main(version_base=None, config_path="../config", config_name="config")
def sample(cfg: DictConfig):
    dataset_name = cfg.loading.name
    engine = cfg.synthesizing.engine
    
    model_path = Path("models") / f"{dataset_name}_{engine}.pkl"
    
    if not model_path.exists():
        print(f"Model not found at {model_path}")
        return

    print(f"Loading model from {model_path}...")
    with open(model_path, "rb") as f:
        synth = dill.load(f)
    
    # We need to know how many samples to generate. 
    # Usually it's the same as the original dataset size.
    # For now, let's just sample 100 rows.
    num_samples = 100
    print(f"Sampling {num_samples} rows...")
    synthetic_df = synth.sample(num_samples)
    
    # Ensure it's a DataFrame
    if not isinstance(synthetic_df, pd.DataFrame):
        synthetic_df = pd.DataFrame(synthetic_df)
    
    output_dir = Path("synthetic_data")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{dataset_name}_{engine}_synthetic.csv"
    
    synthetic_df.to_csv(output_path, index=False)
    print(f"Synthetic data saved to {output_path}")
    print("First 5 rows:")
    print(synthetic_df.head())

if __name__ == "__main__":
    sample()
