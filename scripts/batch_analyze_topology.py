import igraph as ig
import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
import time

def parse_filename(filename):
    """
    Parses metadata from filenames like:
    adult_adult_aim_eps0.1_graph.graphml
    census_census_mst_eps1.0_graph.graphml
    """
    # Remove extension
    stem = filename.replace("_graph.graphml", "")
    
    # Try to find epsilon
    eps_match = re.search(r"eps([\d\.]+)", stem)
    eps = float(eps_match.group(1)) if eps_match else None
    
    # Common algorithms
    algorithms = ["aim", "mst", "patectgan", "co_noise"]
    found_alg = "unknown"
    for alg in algorithms:
        if alg in stem:
            found_alg = alg
            break
            
    # Dataset name (usually the first or second part)
    parts = stem.split("_")
    if parts[0] == "graph" and len(parts) > 1:
        dataset = parts[1]
    else:
        dataset = parts[0]
    
    return dataset, found_alg, eps

def analyze_graph(file_path):
    print(f"Processing {file_path}...", flush=True)
    try:
        g = ig.Graph.Read_GraphML(str(file_path))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

    dataset, algorithm, eps = parse_filename(file_path.name)
    
    # Core stats
    n_nodes = g.vcount()
    n_edges = g.ecount()
    
    degrees = np.array(g.degree())
    active_degrees = degrees[degrees > 0]
    n_active_nodes = len(active_degrees)
    
    if n_active_nodes == 0:
        return {
            "dataset": dataset, "algorithm": algorithm, "eps": eps,
            "n_nodes": n_nodes, "n_edges": n_edges, "n_active": 0,
            "max_degree": 0, "min_degree": 0, "avg_degree": 0, "var_degree": 0,
            "density": 0, "n_components": 0, "giant_size": 0, "max_clique": 0,
            "avg_eigenvector_centrality": 0
        }

    # Connectivity
    components = g.connected_components()
    n_components = len(components)
    giant_size = len(components.giant().vs) if n_components > 0 else 0
    
    # Degree stats
    max_deg = np.max(degrees)
    min_deg = np.min(degrees)
    avg_deg = np.mean(degrees)
    var_deg = np.var(degrees)
    
    # Density
    density = g.density()
    
    # Clique number (can be slow, but usually okay for these graphs)
    try:
        # We limit to a timeout or simple check if it's too large
        if n_edges < 100000:
            max_clique = g.clique_number()
        else:
            max_clique = -1 # Too expensive
    except:
        max_clique = -1
        
    # Centrality (Eigenvector is generally fast and informative)
    try:
        ev_cent = g.eigenvector_centrality()
        avg_ev = np.mean(ev_cent)
    except:
        avg_ev = -1

    return {
        "dataset": dataset,
        "algorithm": algorithm,
        "eps": eps,
        "filename": file_path.name,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "n_active": n_active_nodes,
        "max_degree": int(max_deg),
        "min_degree": int(min_deg),
        "avg_degree": float(avg_deg),
        "var_degree": float(var_deg),
        "density": float(density),
        "n_components": n_components,
        "giant_size": giant_size,
        "rel_giant_size": giant_size / n_nodes if n_nodes > 0 else 0,
        "max_clique": max_clique,
        "avg_eigenvector_centrality": avg_ev
    }

def main():
    graph_dir = Path("outputs/graphs")
    output_file = "outputs/graph_topology_summary.csv"
    
    if not graph_dir.exists():
        print(f"Directory {graph_dir} does not exist.", flush=True)
        return

    graph_files = list(graph_dir.glob("*.graphml"))
    print(f"Found {len(graph_files)} graphs initially.", flush=True)
    
    # Filter out eps=0.001 early to avoid massive wait times
    filtered_files = []
    for f in graph_files:
        _, _, eps = parse_filename(f.name)
        if eps == 0.001:
            print(f"Skipping {f.name} (eps=0.001 is too large)", flush=True)
            continue
        filtered_files.append(f)
        
    print(f"Proceeding with {len(filtered_files)} graphs.", flush=True)
    
    results = []
    for i, f in enumerate(filtered_files):
        print(f"[{i+1}/{len(filtered_files)}] ", end="", flush=True)
        res = analyze_graph(f)
        if res:
            results.append(res)
            
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}", flush=True)

if __name__ == "__main__":
    main()
