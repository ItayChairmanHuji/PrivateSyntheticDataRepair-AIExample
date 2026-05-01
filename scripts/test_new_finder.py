
import pandas as pd
from src.loading.file_loader import FileLoader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder
from src.loading.violation_finder import ViolationFinder
import os

def test_all_datasets():
    datasets = ["adult100", "dummy", "custom_violations", "compas", "census", "tax"]
    
    for ds_name in datasets:
        print(f"\n--- Testing Dataset: {ds_name} ---")
        loader = FileLoader(
            name=ds_name, 
            base_path="data",
            data_loader=DataLoader(),
            dcs_loader=DCsLoader(),
            metadata_loader=MetadataLoader(),
            data_encoder=DataEncoder(),
            dcs_encoder=DCsEncoder()
        )
        try:
            dataset = loader.load()
            # Dataset will trigger ViolationFinder via DuckDB
            violations = dataset.get_violations()
            print(f"Success! Found {len(violations)} violations.")
            if len(violations) > 0:
                print(violations.head(2))
        except Exception as e:
            print(f"Failed to process {ds_name}: {e}")

if __name__ == "__main__":
    test_all_datasets()
