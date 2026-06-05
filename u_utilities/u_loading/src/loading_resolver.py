from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoadingResolver:
    base_path: str
    dataset_name: str

    @property
    def dataset_dir(self) -> Path:
        return Path(self.base_path) / self.dataset_name / "base"

    @property
    def data_path(self) -> Path:
        return self.dataset_dir / "original_data.csv"

    @property
    def dcs_path(self) -> Path:
        return self.dataset_dir / "dcs.txt"

    @property
    def metadata_path(self) -> Path:
        return self.dataset_dir / "metadata.json"
