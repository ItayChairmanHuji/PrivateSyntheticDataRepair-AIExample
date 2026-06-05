import pandas as pd
from pathlib import Path
from typing import Optional
from u_utilities.u_shared import Dataset
from .base import Loader
from .dcs_loader import DCsLoader
from .metadata_loader import MetadataLoader

class DataLoader(Loader):
    def __init__(self):
        self.dc_loader = DCsLoader()
        self.meta_loader = MetadataLoader()

    def load(self, path: Path, context_dir: Optional[Path] = None) -> Dataset:
        data_path = path if path.suffix == ".csv" else path / "data.csv"
        source_dir = context_dir or self._discover_context(path)
        
        meta = self.meta_loader.load(source_dir / "metadata.json")
        dcs = self.dc_loader.load(source_dir / "dcs.txt")
        data = pd.read_csv(data_path)
        
        return Dataset(
            name=meta.get("name", source_dir.parent.name),
            data=data,
            dcs=dcs,
            target=meta.get("target", ""),
            mappings=meta.get("mappings")
        )

    def save(self, dataset: Dataset, dir_path: Path) -> None:
        dir_path.mkdir(parents=True, exist_ok=True)
        dataset.data.to_csv(dir_path / "data.csv", index=False)
        
        meta = {
            "name": dataset.name,
            "target": dataset.target,
            "columns": list(dataset.data.columns),
            "mappings": self._serialize_mappings(dataset.mappings)
        }
        self.meta_loader.save(meta, dir_path / "metadata.json")
        self.dc_loader.save(dataset.dcs, dir_path / "dcs.txt")

    def _discover_context(self, path: Path) -> Path:
        for parent in [path] + list(path.parents):
            if parent.parent.name == "r_data":
                return parent / "private"
        return path if path.is_dir() else path.parent

    def _serialize_mappings(self, mappings):
        if not mappings: return {}
        # If it's already a serializable dict, return it
        if all(not hasattr(v, 'classes_') for v in mappings.values()):
            return mappings
        # Otherwise, assume they are LabelEncoders and serialize them
        return {
            col: {str(label): int(idx) for idx, label in enumerate(le.classes_)}
            for col, le in mappings.items() if hasattr(le, 'classes_')
        }
