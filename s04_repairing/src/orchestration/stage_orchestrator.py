from dataclasses import dataclass
from s04_repairing.src.io import FileLoader, ArtifactSaver
from s04_repairing.src.repair.repairer import Repairer

@dataclass
class StageOrchestrator:
    experiment_name: str
    repairer: Repairer
    loader: FileLoader
    saver: ArtifactSaver

    def run(self):
        print(f"--- Stage 4: Repairing Synthetic Data [{self.experiment_name}] ---")
        
        # 1. Load artifacts
        dataset, marginals = self.loader.load()
        
        # 2. Repair
        print(f"Repairing using {self.repairer.__class__.__name__}...")
        repaired_dataset = self.repairer.repair(dataset, marginals)
        
        # 3. Save
        self.saver.save(repaired_dataset)
