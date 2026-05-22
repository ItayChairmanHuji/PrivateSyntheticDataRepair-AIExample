from dataclasses import dataclass
from pathlib import Path
from s01_loading.src.io import ArtifactSaver

@dataclass
class StageOrchestrator:
    loader: any
    output_dir: Path

    def run(self):
        dataset = self.loader.load()
        saver = ArtifactSaver(self.output_dir)
        saver.save(dataset)
        return dataset
