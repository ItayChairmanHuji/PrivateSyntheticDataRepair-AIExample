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
        import time
        print(f"--- Stage 4: Repairing Synthetic Data [{self.experiment_name}] ---")
        
        # 1. Load artifacts
        dataset, marginals = self.loader.load()
        
        # 2. Repair
        print(f"Repairing using {self.repairer.__class__.__name__}...")
        start_time = time.time()
        repaired_dataset = self.repairer.repair(dataset, marginals)
        end_time = time.time()
        runtime = end_time - start_time
        print(f"Repair completed in {runtime:.2f}s")
        
        # 3. Collect extra metadata (like iteration stats)
        extra_metadata = {}
        if hasattr(self.repairer, "iteration_stats"):
            extra_metadata["iteration_stats"] = self.repairer.iteration_stats
        
        # 4. Save
        self.saver.save(repaired_dataset, runtime=runtime, extra_metadata=extra_metadata)
