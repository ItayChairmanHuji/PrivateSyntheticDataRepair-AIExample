from dataclasses import dataclass
from .engine import LoadingEngine
from .core.loading_core import LoadingCore

@dataclass
class LoadingWorker:
    """Orchestrator: Coordinates the Engine and Logic for the loading process."""
    engine: LoadingEngine
    core: LoadingCore

    def run(self):
        """Executes the loading flow: Load -> Resolve -> Save."""
        # 1. Use Logic to load the data from raw sources
        dataset = self.core.load()
        
        # 2. Use the Engine to resolve where to save
        output_dir = self.engine.resolve_output_dir(dataset.name)

        # 3. Use the Engine to save the output
        self.engine.save_dataset(dataset, output_dir)
        
        print(f"Success [p01_loading]: {dataset.name} -> {output_dir}")
