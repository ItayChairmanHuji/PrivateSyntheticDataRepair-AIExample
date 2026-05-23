from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from s02_synthesizing.src.io.artifact_saver import ArtifactSaver
from s02_synthesizing.src.io.input_loader import InputLoader
from shared.entities.dataset import Dataset


@dataclass
class StageOrchestrator:
    synthesizer: any
    output_dir: Path
    mode: str = "full"
    input_root: Path = Path("s02_synthesizing/input")

    def run(self) -> Optional[Dataset]:
        """
        Executes the synthesis stage based on the specified mode.
        """
        dataset_name = self.output_dir.name
        input_dir = self.input_root / dataset_name

        # 1. Load artifacts from Stage 1
        loader = InputLoader(input_dir)
        dataset = loader.load()

        # 2. Run synthesis/training/sampling
        synthetic_dataset = self._execute_synthesis(dataset)

        # 3. Save artifacts if synthesis occurred
        if synthetic_dataset:
            saver = ArtifactSaver(self.output_dir)
            saver.save(synthetic_dataset, self.synthesizer, self.mode)
            return synthetic_dataset

        return None

    def _execute_synthesis(self, dataset: Dataset) -> Optional[Dataset]:
        match self.mode:
            case "train":
                return self._train(dataset)
            case "sample":
                return self._sample(dataset)
            case _:
                return self._full_synthesis(dataset)

    def _train(self, dataset: Dataset):
        print("Running training only mode...")
        if hasattr(self.synthesizer, "fit_and_save"):
            self.synthesizer.fit_and_save(dataset)
        else:
            self.synthesizer.synthesize(dataset)
        return None

    def _sample(self, dataset: Dataset):
        print("Running sampling only mode...")
        return (
            self.synthesizer.sample(dataset)
            if hasattr(self.synthesizer, "sample")
            else self.synthesizer.synthesize(dataset)
        )

    def _full_synthesis(self, dataset: Dataset):
        print("Running full synthesis mode...")
        return self.synthesizer.synthesize(dataset)
