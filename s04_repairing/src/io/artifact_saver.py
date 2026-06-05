from dataclasses import dataclass
from pathlib import Path
from shared.entities.dataset import Dataset

@dataclass
class ArtifactSaver:
    experiment_name: str
    base_path: str = "s04_repairing/output"

    def save(self, dataset: Dataset, runtime: float = None, extra_metadata: dict = None):
        output_dir = Path(self.base_path) / self.experiment_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "repaired_data.csv"
        dataset.data.to_csv(output_path, index=False)
        
        import json
        from shared.utils.serialization_helper import NpEncoder
        metadata_path = output_dir / "metadata.json"
        metadata = {
            "name": dataset.name,
            "target": dataset.target,
            "repair_runtime": runtime if runtime is not None else 0.0
        }
        if extra_metadata:
            metadata.update(extra_metadata)
            
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4, cls=NpEncoder)
        print(f"Success: Metadata saved to {metadata_path}")

        print(f"Success: Repaired dataset saved to {output_path}")
