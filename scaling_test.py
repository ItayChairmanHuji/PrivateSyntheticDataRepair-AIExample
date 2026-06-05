import pandas as pd
import time
from shared.entities.dataset import Dataset
import os

def stress_test_violations():
    print("--- Scaling Test: 300K Synthetic Records (Value-Grouped) ---")
    
    synthetic_path = "s02_synthesizing/output/adult/synthetic_data.csv"
    if not os.path.exists(synthetic_path):
        print(f"Error: {synthetic_path} not found.")
        return
    
    print(f"Loading {synthetic_path}...")
    data = pd.read_csv(synthetic_path)
    print(f"Loaded {len(data)} rows.")
    
    # Load constraints manually
    from s01_loading.src.loaders import DCsLoader, MetadataLoader
    from s01_loading.src.encoders import DCsEncoder, DataEncoder
    
    dcs_loader = DCsLoader()
    raw_dcs = dcs_loader.load("data/adult/dcs.txt")
    
    data_encoder = DataEncoder()
    dcs_encoder = DCsEncoder()
    metadata_loader = MetadataLoader()
    
    metadata = metadata_loader.load("data/adult/metadata.json")
    real_data = pd.read_csv("data/adult/data.csv")
    data_encoder.encode(real_data)
    encoded_dcs = dcs_encoder.encode(raw_dcs, data_encoder.mappings)
    
    dataset_300k = Dataset(
        name="adult_300k",
        data=data,
        dcs=encoded_dcs,
        target=metadata.get("target", "")
    )
    
    print(f"Detecting violations using Value-Grouped Symbolic Conflict Graph...")
    start_time = time.time()
    
    from shared.utils.violation_finder.value_grouped_engine import ValueGroupedEngine
    engine = ValueGroupedEngine()
    
    all_bicliques = []
    for dc in encoded_dcs.constraints:
        dc_start = time.time()
        res_bc = engine.find_violations(data, dc)
        dc_end = time.time()
        print(f"DC: {dc.to_string()}")
        print(f"  - Unique value groups: {len(res_bc.group_indices)}")
        print(f"  - Bicliques found: {len(res_bc.bicliques)}")
        print(f"  - Time taken: {dc_end - dc_start:.2f}s")
        all_bicliques.extend(res_bc.bicliques)
    
    from shared.entities.violations import BicliqueCollection
    
    # Create collection with all bicliques
    # The graph will now automatically handle the different groupings!
    global_bc = BicliqueCollection(bicliques=all_bicliques)
    
    print(f"Constructing Multi-Group Symbolic Conflict Graph...")
    from s04_repairing.src.repair.symbolic_graph import SymbolicConflictGraph
    graph = SymbolicConflictGraph(len(data), global_bc)
    
    print(f"Done! Graph constructed.")
    print(f"Graph vertex count: {graph.n}")
    print(f"Number of distinct groupings in graph: {len(graph._group_active_counts)}")
    
    # Test a few degrees to ensure correctness
    print(f"Sample degrees for first 5 nodes: {graph.degree(range(5))}")
    
    end_time = time.time()
    print(f"Total time (full pipeline): {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    stress_test_violations()
