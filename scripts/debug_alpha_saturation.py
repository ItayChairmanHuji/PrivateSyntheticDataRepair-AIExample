import pandas as pd
import numpy as np
import igraph as ig
import os
import sys
import json
from src.loading.dcs_loader import load_dcs
from src.entities.dataset import Dataset
from src.synthesizing.model_loader import SmartNoiseModelLoader
from src.marginals_obtaining.top_k_obtainer import TopKObtainer
from src.marginals_obtaining.utility_functions.distance_utility import DistanceUtility

def debug_saturation(dataset_name, model_type="aim", eps=0.1):
    print(f"\n=== Debugging Alpha Saturation: {dataset_name} ===")
    
    data_path = f"data/{dataset_name}/data.csv"
    dcs_path = f"data/{dataset_name}/dcs.txt"
    model_path = f"models/{dataset_name}_{model_type}_eps{eps}.pkl"
    
    if not os.path.exists(model_path):
        model_path = f"models/{dataset_name}_{model_type}.pkl"
        if not os.path.exists(model_path):
            print(f"Skipping {dataset_name}: Model not found")
            return

    data = pd.read_csv(data_path)
    if len(data) > 50000:
        data = data.sample(50000, random_state=42).reset_index(drop=True)
        print(f"Sampled to 50k tuples.")

    dcs = load_dcs(dcs_path)
    metadata_path = f"data/{dataset_name}/metadata.json"
    target = "None"
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            target = json.load(f).get("target", "None")

    original_ds = Dataset(name=dataset_name, data=data, dcs=dcs, target=target)
    
    print(f"Generating synthetic data...")
    loader = SmartNoiseModelLoader(model_path=model_path, seed=42)
    synthetic_ds = loader.synthesize(original_ds)
    
    print(f"Obtaining top-20 marginals...")
    obtainer = TopKObtainer(selection_budget=1000, generation_budget=1000, k=20, utility_function=DistanceUtility())
    marginals = obtainer.obtain(original_ds, synthetic_ds)
    
    print(f"Finding violations...")
    violations = synthetic_ds.get_violations()
    n_tuples = len(synthetic_ds.data)
    
    if violations.empty:
        print("No violations found.")
        return

    # Build graph
    edges = list(zip(violations['idx1'].astype(int), violations['idx2'].astype(int)))
    g = ig.Graph(n_tuples, edges)
    g.simplify()
    
    degrees = np.array(g.degree())
    active_indices = np.where(degrees > 0)[0]
    
    # Analyze record-marginal matching
    print(f"Analyzing record-marginal matches for {len(active_indices)} active records...")
    match_counts = []
    for idx in active_indices:
        tuple_data = synthetic_ds.data.iloc[[idx]]
        count = 0
        for m in marginals:
            if m.get_mask(tuple_data).iloc[0]:
                count += 1
        match_counts.append(count)
    
    match_counts = np.array(match_counts)
    print(f"Match Statistics (per active record):")
    print(f"  - Mean matches: {np.mean(match_counts):.2f}")
    print(f"  - Max matches: {np.max(match_counts)}")
    print(f"  - records matching 0 marginals: {np.sum(match_counts == 0)} ({np.sum(match_counts == 0)/len(active_indices):.2%})")
    
    # Weight variance analysis (Simulating the first step of WeightedVCRepairer)
    # We don't need the exact weight values, just to see if they differ
    C = np.zeros(len(marginals))
    T = np.array([m.target for m in marginals])
    for i, m in enumerate(marginals):
        mask = m.get_mask(synthetic_ds.data)
        C[i] = mask.sum()
    
    N_prime = n_tuples - 1
    coeff = 1 / len(marginals)
    base_diffs = np.abs(C / N_prime - T)
    base_sum = base_diffs.sum()
    hypo_diffs = np.abs((C - 1) / N_prime - T)
    diff_gain = hypo_diffs - base_diffs
    
    weights = []
    for idx in active_indices:
        # Check which marginals this tuple matches
        tuple_data = synthetic_ds.data.iloc[[idx]]
        match_indices = [i for i, m in enumerate(marginals) if m.get_mask(tuple_data).iloc[0]]
        if match_indices:
            w = coeff * (base_sum + diff_gain[match_indices].sum())
        else:
            w = coeff * base_sum
        weights.append(w)
    
    weights = np.array(weights)
    print(f"Weight Statistics:")
    print(f"  - Unique weights: {len(np.unique(weights))}")
    print(f"  - Weight StdDev: {np.std(weights):.2e}")
    
    # Degree variance analysis
    active_degrees = degrees[active_indices]
    print(f"Degree Statistics:")
    print(f"  - Unique degrees: {len(np.unique(active_degrees))}")
    print(f"  - Mean degree: {np.mean(active_degrees):.2f}")

if __name__ == "__main__":
    for ds in ["compas", "tax"]:
        try:
            debug_saturation(ds)
        except Exception as e:
            print(f"Error analyzing {ds}: {e}")
