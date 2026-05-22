from dataclasses import dataclass
from pathlib import Path
from shared.entities.dataset import Dataset

@dataclass
class ArtifactSaver:
    dataset_name: str
    base_path: str = "s04_repairing/output"

    def save(self, dataset: Dataset):
        output_dir = Path(self.base_path) / self.dataset_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / "repaired_data.csv"
        dataset.data.to_csv(output_path, index=False)
        print(f"Success: Repaired dataset saved to {output_path}")
