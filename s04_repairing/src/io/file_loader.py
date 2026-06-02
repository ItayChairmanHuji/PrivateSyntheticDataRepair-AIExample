from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s01_loading.src.loaders import DataLoader, DCsLoader, MetadataLoader
from s04_repairing.src.loaders import MarginalsLoader

@dataclass
class FileLoader:
    experiment_name: str
    base_path: str = "s04_repairing/input"
    data_loader: DataLoader = DataLoader()
    dcs_loader: DCsLoader = DCsLoader()
    metadata_loader: MetadataLoader = MetadataLoader()
    marginals_loader: MarginalsLoader = MarginalsLoader()

    def load(self) -> Tuple[Dataset, MarginalSet]:
        data_path = self.input_dir / "synthetic_data.csv"
        dcs_path = self.input_dir / "constraints.txt"
        metadata_path = self.input_dir / "metadata.json"
        marginals_path = self.input_dir / "marginals.json"

        data = self.data_loader.load(data_path)
        dcs = self.dcs_loader.load(dcs_path)
        metadata = self.metadata_loader.load(metadata_path)
        marginals = self.marginals_loader.load(marginals_path)

        dataset = Dataset(
            name=metadata["name"] + "_syn",
            data=data,
            dcs=dcs,
            target=metadata["target"],
            mappings=metadata.get("mappings")
        )
        return dataset, marginals

    @property
    def input_dir(self) -> Path:
        return Path(self.base_path) / self.experiment_name
