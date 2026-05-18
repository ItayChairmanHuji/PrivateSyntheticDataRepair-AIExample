import pandas as pd
import numpy as np
import igraph as ig
import time
import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from src.loading.dcs_loader import load_dcs
from src.entities.dataset import Dataset
from src.synthesizing.model_loader import SmartNoiseModelLoader

def analyze_topology(dataset_name, model_type="aim", eps=0.1):
    log_file = f"topology_{dataset_name}.log"
    with open(log_file, "w") as out:
        out.write(f"\n--- Analyzing {dataset_name} ({model_type}, eps={eps}) ---\n")
        start_time = time.time()
        
        data_path = f"data/{dataset_name}/data.csv"
        dcs_path = f"data/{dataset_name}/dcs.txt"
        model_path = f"models/{dataset_name}_{model_type}_eps{eps}.pkl"
        
        if not os.path.exists(model_path):
            model_path = f"models/{dataset_name}_{model_type}.pkl"
            if not os.path.exists(model_path):
                out.write(f"Skipping {dataset_name}: Model not found\n")
                return

        out.write(f"Loading data from {data_path}...\n")
        data = pd.read_csv(data_path)
        
        if len(data) > 100000:
            data = data.sample(100000, random_state=42).reset_index(drop=True)
            out.write(f"Sampled to 100,000 tuples.\n")

        dcs = load_dcs(dcs_path)
        metadata_path = f"data/{dataset_name}/metadata.json"
        target = "None"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                target = json.load(f).get("target", "None")

        original_ds = Dataset(name=dataset_name, data=data, dcs=dcs, target=target)
        
        out.write(f"Generating synthetic data from {model_path}...\n")
        loader = SmartNoiseModelLoader(model_path=model_path, seed=42)
        synthetic_ds = loader.synthesize(original_ds)
        
        out.write(f"Finding violations...\n")
        v_start = time.time()
        violations = synthetic_ds.get_violations()
        v_end = time.time()
        
        n_tuples = len(synthetic_ds.data)
        n_violations = len(violations)
        
        out.write(f"Tuples: {n_tuples}\n")
        out.write(f"Violations: {n_violations}\n")
        out.write(f"Violation finding took {v_end - v_start:.2f}s\n")
        
        if n_violations == 0:
            out.write("No violations found in synthetic data.\n")
            return

        out.write(f"Building conflict graph...\n")
        g_start = time.time()
        edges = list(zip(violations['idx1'].astype(int), violations['idx2'].astype(int)))
        g = ig.Graph(n_tuples, edges)
        g.simplify()
        g_end = time.time()
        out.write(f"Graph building took {g_end - g_start:.2f}s\n")
        
        degrees = g.degree()
        max_degree = np.max(degrees)
        active_degrees = [d for d in degrees if d > 0]
        nodes_with_violations = len(active_degrees)
        mean_degree_active = np.mean(active_degrees)
        median_degree_active = np.median(active_degrees)
        
        out.write(f"Nodes with Violations: {nodes_with_violations} ({nodes_with_violations/n_tuples:.2%})\n")
        out.write(f"Max Degree: {max_degree}\n")
        out.write(f"Mean Degree (active nodes): {mean_degree_active:.2f}\n")
        out.write(f"Median Degree (active nodes): {median_degree_active:.2f}\n")
        
        out.write(f"Performing component analysis...\n")
        c_start = time.time()
        components = g.connected_components()
        n_components = len(components)
        giant = components.giant()
        largest_component_size = len(giant.vs)
        c_end = time.time()
        out.write(f"Component analysis took {c_end - c_start:.2f}s\n")
        
        out.write(f"Connected Components: {n_components}\n")
        out.write(f"Largest Component Size: {largest_component_size} ({largest_component_size/n_tuples:.2%})\n")
        
        top_1_percent_count = int(max(1, nodes_with_violations * 0.01))
        top_degrees = sorted(active_degrees, reverse=True)[:top_1_percent_count]
        edges_covered_by_top_1 = sum(top_degrees)
        
        out.write(f"Top 1% active nodes ({top_1_percent_count}) have mean degree: {np.mean(top_degrees):.2f}\n")
        out.write(f"Top 1% active nodes account for approx {edges_covered_by_top_1 / (2 * n_violations):.2%} of edge endpoints.\n")
        
        out.write(f"Total analysis for {dataset_name} took {time.time() - start_time:.2f}s\n")
    
    # Print the log file to stdout so it shows up in Slurm logs
    with open(log_file, "r") as f:
        print(f.read())

if __name__ == "__main__":
    datasets = ["compas", "tax", "adult", "census"]
    for ds in datasets:
        try:
            analyze_topology(ds, model_type="aim", eps=0.1)
        except Exception as e:
            print(f"Failed to analyze {ds}: {e}")
            import traceback
            traceback.print_exc()
