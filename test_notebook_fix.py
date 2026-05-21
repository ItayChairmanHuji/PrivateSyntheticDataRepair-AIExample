import pandas as pd
import numpy as np
import os
import sys
import json
sys.path.append('.')

from src.loading.dcs_loader import load_dcs
from src.entities.dataset import Dataset
from src.synthesizing.model_loader import SmartNoiseModelLoader
from src.marginals_obtaining.top_k_obtainer import TopKObtainer
from src.marginals_obtaining.utility_functions.distance_utility import DistanceUtility
from src.repairing.weighted_vc_repairer import WeightedVCRepairer
from src.utils.mbi_patch import apply_patch

def test_notebook_logic():
    apply_patch()

    dataset_name = "adult"
    data = pd.read_csv(f"data/{dataset_name}/data.csv").head(100) # Even smaller sample
    dcs = load_dcs(f"data/{dataset_name}/dcs.txt")

    with open(f"data/{dataset_name}/metadata.json") as f:
        metadata = json.load(f)
    target = metadata['target']

    ds = Dataset(name=dataset_name, data=data, dcs=dcs, target=target)

    model_path = f"models/{dataset_name}_aim.pkl"
    if os.path.exists(model_path):
        loader = SmartNoiseModelLoader(model_path=model_path, seed=42)
        sds = loader.synthesize(ds)
        
        obtainer = TopKObtainer(1.0, 1.0, 5, DistanceUtility())
        marginals = obtainer.obtain(ds, sds)
        print(f"Obtained {len(marginals)} marginals.")

        print("Running repair with fixed alpha=0.5...")
        repairer_fixed = WeightedVCRepairer(alpha=0.5, use_adaptive_alpha=False)
        res_fixed = repairer_fixed.repair(sds, marginals)
        
        print("\nRunning repair with adaptive alpha...")
        repairer_adaptive = WeightedVCRepairer(alpha=0.5, use_adaptive_alpha=True)
        res_adaptive = repairer_adaptive.repair(sds, marginals)
        
        print(f"\nFixed Alpha Deletions: {len(sds.data) - len(res_fixed.data)}")
        print(f"Adaptive Alpha Deletions: {len(sds.data) - len(res_adaptive.data)}")
    else:
        print(f"Model path {model_path} does not exist.")

if __name__ == "__main__":
    test_notebook_logic()
