import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from shared.entities.dataset import Dataset
from s01_loading.src.loaders.dcs_loader import DCsLoader
from s02_synthesizing.src.io.artifact_saver import ArtifactSaver

@dataclass
class StageOrchestrator:
    synthesizer: any
    dataset_name: str
    mode: str = "full"
    input_root: Path = Path("s02_synthesizing/input")
    output_root: Path = Path("s02_synthesizing/output")

    def run(self) -> Optional[Dataset]:
        """
        Executes the synthesis stage based on the specified mode.
        """
        input_dir = self.input_root / self.dataset_name
        output_dir = self.output_root / self.dataset_name
        
        # 1. Load artifacts from Stage 1
        dataset = self._load_input_dataset(input_dir)
        
        # 2. Run synthesis/training/sampling
        synthetic_dataset = self._execute_synthesis(dataset)

        # 3. Save artifacts if synthesis occurred
        if synthetic_dataset:
            saver = ArtifactSaver(output_dir)
            saver.save(synthetic_dataset, self.synthesizer, self.mode)
            return synthetic_dataset
        
        return None

    def _load_input_dataset(self, input_dir: Path) -> Dataset:
        print(f"Loading input artifacts from {input_dir}...")
        data_path = input_dir / "private_data.csv"
        meta_path = input_dir / "metadata.json"
        dcs_path = input_dir / "constraints.txt"

        if not data_path.exists():
            raise FileNotFoundError(f"Private data not found at {data_path}")

        data = pd.read_csv(data_path)
        
        with open(meta_path, "r") as f:
            metadata = json.load(f)
            
        dcs_loader = DCsLoader()
        dcs = dcs_loader.load(dcs_path)
        
        return Dataset(
            name=metadata["name"],
            data=data,
            dcs=dcs,
            target=metadata["target"],
            mappings=metadata.get("mappings")
        )

    def _execute_synthesis(self, dataset: Dataset) -> Optional[Dataset]:
        if self.mode == "train":
            print(f"Running training only mode...")
            if hasattr(self.synthesizer, 'fit_and_save'):
                self.synthesizer.fit_and_save(dataset)
            else:
                self.synthesizer.synthesize(dataset)
            return None
        
        elif self.mode == "sample":
            print(f"Running sampling only mode...")
            if hasattr(self.synthesizer, 'sample'):
                return self.synthesizer.sample(dataset)
            else:
                return self.synthesizer.synthesize(dataset)
        else:
            print(f"Running full synthesis mode...")
            return self.synthesizer.synthesize(dataset)
