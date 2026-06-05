from dataclasses import dataclass
from typing import Optional

from ..engine.sampling_engine import SamplingEngine
from ..workers.sampling_worker import SamplingWorker

@dataclass
class SamplingOrchestrator:
    """Facade: Orchestrates the end-to-end sampling process."""
    engine: SamplingEngine
    worker: SamplingWorker
    dataset_name: str
    engine_name: str
    epsilon: float
    seed: int
    size: Optional[int] = None

    def run(self):
        """Executes the sampling flow: Load Model -> Sample -> Save Data."""
        # Get metadata from private dataset
        dataset = self.engine.manager.load_dataset(self.dataset_name)
        
        # Load the model
        model_path = self.engine.resolve_model_path(
            self.dataset_name, 
            self.engine_name, 
            self.epsilon, 
            self.seed
        )
        model = self.engine.manager.load_model(model_path)
        
        # Determine actual generation size
        gen_size = self.size if self.size is not None else len(dataset.data)
        
        # Sample data
        synthetic_dataset = self.worker.sample(model, dataset, gen_size)
        
        # Save output
        output_path = self.engine.resolve_synthetic_data_path(
            self.dataset_name, 
            self.engine_name, 
            self.epsilon, 
            self.seed,
            gen_size
        )
        
        # Ensure directory exists and save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        synthetic_dataset.data.to_csv(output_path, index=False)
        
        print(f"Success [p02b_sampling]: {self.dataset_name} -> {output_path}")
