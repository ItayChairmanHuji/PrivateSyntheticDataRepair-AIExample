from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from shared.entities.dataset import Dataset
from s01_loading.src.encoders import DataEncoder, DCsEncoder
from s01_loading.src.loaders import DataLoader, DCsLoader, MetadataLoader, Loader

@dataclass
class FileLoader(Loader):
    name: str
    base_path: str
    data_loader: DataLoader
    dcs_loader: DCsLoader
    metadata_loader: MetadataLoader
    data_encoder: DataEncoder
    dcs_encoder: DCsEncoder
    size: Optional[int] = None
    seed: int = 42

    def load(self) -> Dataset:
        data, dcs, metadata = self._load_raw_artifacts()
        encoded_data, encoded_dcs, mappings = self._encode_artifacts(data, dcs)
        
        return Dataset(
            name=self.name,
            data=encoded_data,
            dcs=encoded_dcs,
            target=metadata.get("target", ""),
            mappings=mappings
        )

    def _load_raw_artifacts(self):
        data = self._sample_if_needed(self.data_loader.load(self.data_path))
        dcs = self.dcs_loader.load(self.dcs_path)
        metadata = self.metadata_loader.load(self.metadata_path)
        return data, dcs, metadata

    def _encode_artifacts(self, data, dcs):
        encoded_data = self.data_encoder.encode(data)
        mappings = self.data_encoder.mappings
        encoded_dcs = self.dcs_encoder.encode(dcs, mappings)
        return encoded_data, encoded_dcs, mappings

    def _sample_if_needed(self, data):
        if self.size is not None and self.size < len(data):
            return data.sample(n=self.size, random_state=self.seed).reset_index(drop=True)
        return data

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
