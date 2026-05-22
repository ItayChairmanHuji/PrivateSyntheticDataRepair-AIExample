import json
from dataclasses import dataclass
from pathlib import Path
from shared.entities.dataset import Dataset

@dataclass
class ArtifactSaver:
    output_dir: Path

    def save(self, synthetic_dataset: Dataset, synthesizer: any, mode: str):
        """
        Saves synthetic data and run metadata.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._export_synthetic_data(synthetic_dataset.data)
        self._export_run_config(synthetic_dataset, synthesizer, mode)
        # Carry over metadata and constraints for downstream stages
        self._export_metadata(synthetic_dataset)
        self._export_constraints(synthetic_dataset.dcs)

    def _export_synthetic_data(self, data):
        data.to_csv(self.output_dir / "synthetic_data.csv", index=False)

    def _export_run_config(self, dataset: Dataset, synthesizer: any, mode: str):
        run_config = {
            "engine": getattr(synthesizer, "engine", "unknown"),
            "epsilon": getattr(synthesizer, "epsilon", None),
            "seed": getattr(synthesizer, "seed", None),
            "size": len(dataset.data),
            "mode": mode
        }
        self._write_json(run_config, "run_config.json")

    def _export_metadata(self, dataset: Dataset):
        metadata = {
            "name": dataset.name,
            "target": dataset.target,
            "columns": list(dataset.data.columns),
            "mappings": dataset.mappings # Mappings are already serialized in the entity or should be handled
        }
        # Note: If mappings are complex (LabelEncoders), they might need serialization help.
        # But for now, we assume they are passed through correctly.
        self._write_json(metadata, "metadata.json")

    def _export_constraints(self, dcs):
        with open(self.output_dir / "constraints.txt", "w") as f:
            f.write(dcs.to_string())

    def _write_json(self, data, filename):
        with open(self.output_dir / filename, "w") as f:
            json.dump(data, f, indent=4)
