from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from src.entities.dataset import Dataset, DatasetWithViolations
from src.loading.loader import Loader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder

@dataclass
class FileLoader(Loader):
    name: str
    base_path: str
    data_loader: DataLoader
    dcs_loader: DCsLoader
    metadata_loader: MetadataLoader
    data_encoder: DataEncoder
    dcs_encoder: DCsEncoder

    def load(self) -> DatasetWithViolations:
        # Orchestration logic
        raw_data = self.data_loader.load(self.data_path)
        raw_dcs = self.dcs_loader.load(self.dcs_path)
        metadata = self.metadata_loader.load(self.metadata_path)
        
        # Ensure "all data is numbers"
        encoded_data = self.data_encoder.encode(raw_data)
        mappings = self.data_encoder.get_mappings()
        
        # Encode DCs to match the numeric data
        encoded_dcs = self.dcs_encoder.encode(raw_dcs, mappings)
        
        target = metadata.get("target", "")
        
        return DatasetWithViolations(
            name=self.name, 
            data=encoded_data, 
            dcs=encoded_dcs, 
            target=target,
            mappings=mappings
        )

    @property
    def data_dir_path(self) -> Path:
        return Path(self.base_path) / self.name

    @property
    def data_path(self) -> Path:
        return self.data_dir_path / "data.csv"

    @property
    def dcs_path(self) -> Path:
        return self.data_dir_path / "dcs.txt"

    @property
    def metadata_path(self) -> Path:
        return self.data_dir_path / "metadata.json"
