from pathlib import Path
from s01_loading.src.components.io import ArtifactSaver

class StageOrchestrator:
    """Orchestrates the execution of Stage 1: Loading."""
    
    def __init__(self, loader, output_dir: Path):
        self.loader = loader
        self.output_dir = output_dir

    def run(self):
        """Executes the loading and saving flow."""
        dataset = self.loader.load()
        
        saver = ArtifactSaver(self.output_dir)
        saver.save(dataset)
        
        return dataset
