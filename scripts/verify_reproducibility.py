import hydra
import pandas as pd
import numpy as np
from pathlib import Path
import torch
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.synthesizing.model_loader import SmartNoiseModelLoader

def test_reproducibility():
    model_path = "models/adult100_mst.pkl"
    seed = 42
    size = 50

    # Mock dataset for metadata
    from src.entities.denial_constraints import DenialConstraints
    from src.entities.dataset import Dataset
    
    # We need a real dataset for columns if we want it to look right, 
    # but the loader primarily uses the model's internal structure.
    # Let's load the real adult100 metadata if possible.
    
    with hydra.initialize(version_base=None, config_path="../config"):
        cfg = hydra.compose(config_name="config", overrides=["loading=adult", "loading.size=100"])
        loader = hydra.utils.instantiate(cfg.loading)
        dataset = loader.load()

    print(f"Testing reproducibility with model: {model_path}")
    
    loader1 = SmartNoiseModelLoader(model_path=model_path, size=size, seed=seed)
    ds1 = loader1.synthesize(dataset)
    
    loader2 = SmartNoiseModelLoader(model_path=model_path, size=size, seed=seed)
    ds2 = loader2.synthesize(dataset)
    
    try:
        pd.testing.assert_frame_equal(ds1.data, ds2.data)
        print("SUCCESS: Both generations are identical with seed 42.")
    except AssertionError as e:
        print(f"FAILURE: Dataframes differ!\n{e}")
        return False

    # Test different seed
    loader3 = SmartNoiseModelLoader(model_path=model_path, size=size, seed=43)
    ds3 = loader3.synthesize(dataset)
    
    try:
        pd.testing.assert_frame_equal(ds1.data, ds3.data)
        print("FAILURE: Dataframes are identical even with different seeds!")
        return False
    except AssertionError:
        print("SUCCESS: Dataframes differ with different seeds.")
        
    return True

if __name__ == "__main__":
    if test_reproducibility():
        print("\nAll reproducibility tests passed.")
    else:
        sys.exit(1)
