import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.entities.dataset import Dataset
from src.loaders.services import data_encoder
from src.loaders.services.dcs_encoder import encode_dcs
from denial_constraints.loading.dcs_loader import load_dcs


@dataclass
class FileLoader:
    name: str
    base_path: str
    data_encoder: object

    def load(self) -> Dataset:
        metadata = self._load_metadata()
        data, mapping = self._load_data()
        dcs = self._load_dcs(mapping)
        target = metadata.get("target", "")
        return Dataset(name=self.name, data=data, dcs=dcs, target=target)

    @property
    def data_dir_path(self):
        return Path(self.base_path) / self.name

    @property
    def data_path(self):
        return self.data_dir_path / "data.csv"

    @property
    def dcs_path(self):
        return self.data_dir_path / "dcs.txt"

    @property
    def metadata_path(self):
        return self.data_dir_path / "metadata.json"

    def _load_data(self):
        data = pd.read_csv(self.data_path)
        encoded_data, mapping = data_encoder.encode(data)
        return encoded_data, mapping

    def _load_dcs(self, mapping):
        dcs = load_dcs(self.dcs_path)
        return encode_dcs(dcs, mapping)

    def _load_metadata(self):
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)
