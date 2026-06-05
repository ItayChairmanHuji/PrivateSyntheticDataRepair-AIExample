import pandas as pd
import time
from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s04_repairing.src.repair.classic_vc_repairer import ClassicVCRepairer
import os

def stress_test_repair():
    print("--- Scaling Repair Test: 300K Synthetic Records ---")
    
    synthetic_path = "s02_synthesizing/output/adult/synthetic_data.csv"
    if not os.path.exists(synthetic_path):
        print(f"Error: {synthetic_path} not found.")
        return
    
    print(f"Loading {synthetic_path}...")
    data = pd.read_csv(synthetic_path)
    print(f"Loaded {len(data)} rows.")
    
    # Load constraints
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
    
    print(f"Initial violations: {len(dataset_300k.get_violations())}")
    
    # Run Weighted Repair (now optimized with O(1) degree array)
    from s04_repairing.src.repair.weighted_vc_repairer import WeightedVCRepairer
    print(f"Running WeightedVCRepairer...")
    repairer = WeightedVCRepairer(alpha=0.5)
    marginals = MarginalSet([])
    
    # Override VertexCoverRepairer.repair to add logging
    def repair_with_logging(self, dataset, marginals):
        graph = self._build_conflict_graph(dataset)
        it = 0
        while graph.ecount() > 0:
            vertices_to_delete = self._select_vertex(graph, dataset, marginals)
            for v_idx in vertices_to_delete:
                graph.delete_edges(v_idx)
            it += 1
            if it % 1000 == 0:
                print(f"Iteration {it}, Active nodes: {len(graph.active_nodes)}, Approx edges: {graph.ecount()}")
        
        keep_indices = [i for i in range(len(dataset.data)) if i not in graph.deleted_vertices]
        data = dataset.data.iloc[keep_indices].reset_index(drop=True)
        return Dataset(name=f"{dataset.name}_repaired", data=data, dcs=dataset.dcs, target=dataset.target)

    start_time = time.time()
    repaired_ds = repair_with_logging(repairer, dataset_300k, marginals)
    end_time = time.time()
    
    print(f"Repair done in {end_time - start_time:.2f} seconds.")
    print(f"Final dataset size: {len(repaired_ds.data)}")
    
    print("Verifying final violations...")
    v_final = len(repaired_ds.get_violations())
    print(f"Final violations: {v_final}")
    
    if v_final == 0:
        print("SUCCESS: Repair works and scales to 300K rows!")
    else:
        print("FAILURE: Remaining violations found.")

if __name__ == "__main__":
    stress_test_repair()
