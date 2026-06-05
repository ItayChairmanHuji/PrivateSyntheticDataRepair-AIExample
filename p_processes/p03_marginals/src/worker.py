from dataclasses import dataclass
from .engine import MarginalsEngine
from .core.marginals_core import MarginalsCore

@dataclass
class MarginalsWorker:
    """Orchestrator: Connects the Engine and Logic for the marginals process."""
    engine: MarginalsEngine
    core: MarginalsCore
    dataset_name: str
    noise_level: float

    def run(self):
        """Executes the marginals flow: Load Dataset -> Calculate -> Save."""
        # 1. Use the Engine to load the resource
        dataset = self.engine.load_dataset(self.dataset_name)
        
        # 2. Use Logic to perform the calculation
        marginals = self.core.calculate(dataset, noise_level=self.noise_level)
        
        # 3. Use the Engine to save the output
        self.engine.save_marginals(
            marginals, 
            dataset_name=self.dataset_name, 
            noise_level=self.noise_level
        )
        
        print(f"Success [p03_marginals]: {self.dataset_name} (noise={self.noise_level})")
