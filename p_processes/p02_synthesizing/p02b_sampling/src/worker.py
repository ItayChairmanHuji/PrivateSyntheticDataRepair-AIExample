from dataclasses import dataclass
from typing import Optional
from .engine import SamplingEngine
from .core.sampling_core import SamplingCore

@dataclass
class SamplingWorker:
    """Orchestrator: Coordinates the Engine and Logic for the sampling process."""
    engine: SamplingEngine
    core: SamplingCore
    dataset_name: str
    engine_name: str
    epsilon: float
    seed: int
    size: Optional[int] = None

    def run(self):
        """Executes the sampling flow: Load Model -> Sample -> Save Data."""
        # 1. Use the Engine to load the private resource (for metadata)
        dataset = self.engine.manager.load_dataset(self.dataset_name)
        
        # 2. Use the Engine to resolve model path and load it
        model_path = self.engine.resolve_model_path(
            self.dataset_name, 
            self.engine_name, 
            self.epsilon, 
            self.seed
        )
        model = self.engine.manager.load_model(model_path)
        
        # Determine actual generation size
        gen_size = self.size if self.size is not None else len(dataset.data)
        
        # 3. Use Logic to perform sampling
        synthetic_dataset = self.core.sample(model, dataset, gen_size)
        
        # 4. Use the Engine to resolve output path and save
        output_path = self.engine.resolve_synthetic_data_path(
            self.dataset_name, 
            self.engine_name, 
            self.epsilon, 
            self.seed,
            gen_size
        )
        
        # Use the Engine's manager to save
        self.engine.manager.save_dataset(synthetic_dataset, output_path.parent)
        
        print(f"Success [p02b_sampling]: {self.dataset_name} -> {output_path}")
