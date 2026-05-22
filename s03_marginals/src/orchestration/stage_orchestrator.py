from pathlib import Path
from dataclasses import dataclass
from s03_marginals.src.loaders.artifact_loader import ArtifactLoader
from s03_marginals.src.io.artifact_saver import ArtifactSaver
from s03_marginals.src.marginals.obtainer import Obtainer

@dataclass
class StageOrchestrator:
    loader: ArtifactLoader
    saver: ArtifactSaver
    obtainer: Obtainer

    def run(self, dataset_name: str):
        input_dir = Path("s03_marginals/input") / dataset_name
        output_dir = Path("s03_marginals/output") / dataset_name
        
        p_ds, s_ds = self.loader.load(input_dir)
        marginals = self.obtainer.obtain(p_ds, s_ds)
        self.saver.save(marginals, output_dir)
        
        print(f"Success: Obtained {len(marginals.marginals)} marginals.")
