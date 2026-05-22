import pandas as pd
import json
from pathlib import Path
from dataclasses import dataclass
from shared.entities.dataset import Dataset
from s01_loading.src.loaders.dcs_loader import DCsLoader

@dataclass
class ArtifactLoader:
    def load(self, input_dir: Path) -> tuple[Dataset, Dataset]:
        p_data = pd.read_csv(input_dir / "private_data.csv")
        s_data = pd.read_csv(input_dir / "synthetic_data.csv")
        with open(input_dir / "metadata.json", "r") as f:
            metadata = json.load(f)
        dcs = DCsLoader().load(input_dir / "constraints.txt")
        p_ds = Dataset(name=metadata["name"], data=p_data, dcs=dcs, target=metadata["target"])
        s_ds = Dataset(name=metadata.get("name", "syn") + "_syn", data=s_data, dcs=dcs, target=metadata["target"])
        return p_ds, s_ds
