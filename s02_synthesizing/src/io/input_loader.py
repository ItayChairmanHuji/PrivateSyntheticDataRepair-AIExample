import json
import pandas as pd
from pathlib import Path
from shared.entities.dataset import Dataset
from s01_loading.src.loaders.dcs_loader import DCsLoader

class InputLoader:
    def __init__(self, input_dir: Path):
        self.input_dir = input_dir

    def load(self) -> Dataset:
        print(f"Loading input artifacts from {self.input_dir}...")
        data_path = self.input_dir / "private_data.csv"
        meta_path = self.input_dir / "metadata.json"
        dcs_path = self.input_dir / "constraints.txt"

        if not data_path.exists():
            raise FileNotFoundError(f"Private data not found at {data_path}")

        data = pd.read_csv(data_path)
        
        with open(meta_path, "r") as f:
            metadata = json.load(f)
            
        dcs_loader = DCsLoader()
        dcs = dcs_loader.load(dcs_path)
        
        return Dataset(
            name=metadata["name"],
            data=data,
            dcs=dcs,
            target=metadata["target"],
            mappings=metadata.get("mappings")
        )
