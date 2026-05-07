import hydra
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.synthesizing.model_loader import SmartNoiseModelLoader

def check_model_reproducibility(model_path, dataset):
    seed = 42
    size = 50

    print(f"\n--- Testing model: {model_path} ---")
    
    try:
        loader1 = SmartNoiseModelLoader(model_path=model_path, size=size, seed=seed)
        ds1 = loader1.synthesize(dataset)
        
        loader2 = SmartNoiseModelLoader(model_path=model_path, size=size, seed=seed)
        ds2 = loader2.synthesize(dataset)
        
        pd.testing.assert_frame_equal(ds1.data, ds2.data)
        print(f"PASS: Identical results with seed {seed}")

        loader3 = SmartNoiseModelLoader(model_path=model_path, size=size, seed=seed + 1)
        ds3 = loader3.synthesize(dataset)
        
        try:
            pd.testing.assert_frame_equal(ds1.data, ds3.data)
            print(f"FAIL: Identical results with different seeds!")
            return False
        except AssertionError:
            print(f"PASS: Different results with different seeds")
            
        return True
    except Exception as e:
        print(f"ERROR: Exception during testing: {e}")
        return False

def main():
    models_dir = Path("models")
    model_files = list(models_dir.glob("*.pkl"))
    
    # Load adult100 as a base dataset for metadata
    with hydra.initialize(version_base=None, config_path="../config"):
        cfg = hydra.compose(config_name="config", overrides=["loading=adult", "loading.size=100"])
        loader = hydra.utils.instantiate(cfg.loading)
        dataset = loader.load()

    results = {}
    for model_file in model_files:
        success = check_model_reproducibility(str(model_file), dataset)
        results[model_file.name] = "PASS" if success else "FAIL"

    print("\n" + "="*30)
    print("Reproducibility Summary")
    print("="*30)
    for model, status in results.items():
        print(f"{model:30} : {status}")

if __name__ == "__main__":
    main()
