import json
from dataclasses import dataclass
from pathlib import Path
from shared.entities.dataset import Dataset

@dataclass
class ArtifactSaver:
    output_dir: Path

    def save(self, dataset: Dataset):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._export_data(dataset.data)
        self._export_metadata(dataset)
        self._export_constraints(dataset.dcs)

    def _export_data(self, data):
        data.to_csv(self.output_dir / "private_data.csv", index=False)

    def _export_metadata(self, dataset: Dataset):
        metadata = {
            "name": dataset.name,
            "target": dataset.target,
            "columns": list(dataset.data.columns),
            "mappings": self._serialize_mappings(dataset.mappings)
        }
        self._write_json(metadata, "metadata.json")

    def _export_constraints(self, dcs):
        with open(self.output_dir / "constraints.txt", "w") as f:
            f.write(dcs.to_string())

    def _serialize_mappings(self, mappings):
        if not mappings: return {}
        return {
            col: {str(label): int(idx) for idx, label in enumerate(le.classes_)}
            for col, le in mappings.items()
        }

    def _write_json(self, data, filename):
        with open(self.output_dir / filename, "w") as f:
            json.dump(data, f, indent=4)
