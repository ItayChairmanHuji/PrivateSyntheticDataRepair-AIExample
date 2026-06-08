from pathlib import Path
from typing import Optional

import pandas as pd

from u_utilities.u_shared import CompactData, Dataset

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

        dataset = Dataset(
            name=meta.get("name", source_dir.parent.name),
            data=data,
            dcs=dcs,
            target=meta.get("target", ""),
            mappings=meta.get("mappings"),
        )

        # Try to load compact version if it exists in the standard location
        self._try_load_compact(dataset, path)

        return dataset

    def save(self, dataset: Dataset, dir_path: Path) -> None:
        dir_path.mkdir(parents=True, exist_ok=True)
        dataset.data.to_csv(dir_path / "data.csv", index=False)

        meta = {
            "name": dataset.name,
            "target": dataset.target,
            "columns": list(dataset.data.columns),
            "mappings": self._serialize_mappings(dataset.mappings),
        }
        self.meta_loader.save(meta, dir_path / "metadata.json")
        self.dc_loader.save(dataset.dcs, dir_path / "dcs.txt")

        # Save any cached compact versions
        for key, compact in dataset._compact.items():
            self._save_compact(compact, dataset, dir_path)

    def _try_load_compact(self, dataset: Dataset, path: Path):
        from u_utilities.u_io.src.enums import DataMode
        from u_utilities.u_io.src.path_resolver import PathResolver

        resolver = PathResolver()
        attrs = sorted(dataset.dcs.attrs)
        if not attrs:
            return

        # Try to resolve path using resolver if possible
        try:
            # We need to infer the parameters that were used for the data path
            # This is complex, but for common cases:
            dataset_name = dataset.name
            mode = DataMode.PRIVATE
            if "synthetic" in str(path):
                mode = DataMode.SYNTHETIC
            if "repaired" in str(path):
                mode = DataMode.REPAIRED

            # For simplicity, we can look for a 'compact' subfolder in the data directory
            # as a primary fallback, which is what save() does.
            compact_dir = path.parent / "compact" / "_".join(attrs)
            if compact_dir.exists():
                dataset._compact["_".join(attrs)] = CompactData.load(compact_dir)
                return

            # Secondary check: r_resources/r_compact
            # (Note: This would need more params like epsilon, seed etc. which are hard to get from just 'path' here)
        except Exception:
            pass

    def _save_compact(self, compact: CompactData, dataset: Dataset, dir_path: Path):
        # We save it in a 'compact' subfolder relative to where the dataset is saved
        compact_dir = dir_path / "compact" / "_".join(compact.attributes)
        compact.save(compact_dir)

    def _discover_context(self, path: Path) -> Path:
        for parent in [path] + list(path.parents):
            if parent.parent.name == "r_data":
                return parent / "private"
        return path if path.is_dir() else path.parent

    def _serialize_mappings(self, mappings):
        if not mappings:
            return {}
        # If it's already a serializable dict, return it
        if all(not hasattr(v, "classes_") for v in mappings.values()):
            return mappings
        # Otherwise, assume they are LabelEncoders and serialize them
        return {
            col: {str(label): int(idx) for idx, label in enumerate(le.classes_)}
            for col, le in mappings.items()
            if hasattr(le, "classes_")
        }
