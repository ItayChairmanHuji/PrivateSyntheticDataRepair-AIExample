from dataclasses import dataclass
from typing import Optional

import pandas as pd

from u_utilities.u_shared import Dataset
from .encoders import DataEncoder, DCsEncoder
from .loaders import DataLoader, DCsLoader, MetadataLoader
from .loading_resolver import LoadingResolver


@dataclass
class ResourceLoader:
    resolver: LoadingResolver
    data_loader: DataLoader
    dcs_loader: DCsLoader
    metadata_loader: MetadataLoader
    data_encoder: DataEncoder
    dcs_encoder: DCsEncoder
    sample_size: Optional[int] = None
    seed: int = 42

    def load_dataset(self) -> Dataset:
        data, dcs, meta = self._load_raw()
        data = self._sample(data)
        enc_data, enc_dcs = self._encode(data, dcs)
        return Dataset(
            name=self.resolver.dataset_name,
            data=enc_data,
            dcs=enc_dcs,
            target=meta.get("target", ""),
            mappings=self.data_encoder.mappings,
        )

    def _load_raw(self):
        data = self.data_loader.load(self.resolver.data_path)
        dcs = self.dcs_loader.load(self.resolver.dcs_path)
        meta = self.metadata_loader.load(self.resolver.metadata_path)
        return data, dcs, meta

    def _sample(self, data: pd.DataFrame) -> pd.DataFrame:
        if self.sample_size is None or self.sample_size >= len(data):
            return data
        return data.sample(n=self.sample_size, random_state=self.seed).reset_index(drop=True)

    def _encode(self, data, dcs):
        encoded_data = self.data_encoder.encode(data)
        encoded_dcs = self.dcs_encoder.encode(dcs, self.data_encoder.mappings)
        return encoded_data, encoded_dcs
