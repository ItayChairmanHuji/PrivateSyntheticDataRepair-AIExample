import json
from dataclasses import dataclass

from ..engine.marginals_engine import MarginalsEngine
from ..workers.marginals_worker import MarginalsWorker

@dataclass
class MarginalsOrchestrator:
    """Facade: Orchestrates the end-to-end marginals process."""
    engine: MarginalsEngine
    worker: MarginalsWorker
    dataset_name: str
    noise_level: float

    def run(self):
        """Executes the marginals flow: Load Dataset -> Calculate -> Save."""
        # Load the dataset
        dataset = self.engine.manager.load_dataset(self.dataset_name)
        
        # Calculate marginals
        marginals = self.worker.calculate(dataset)
        
        # Save output
        output_path = self.engine.resolve_marginal_path(self.dataset_name, self.noise_level)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON (assuming marginals can be converted to dict)
        with open(output_path, "w") as f:
            if hasattr(marginals, "to_dict"):
                json.dump(marginals.to_dict(), f, indent=4)
            else:
                json.dump(marginals, f, indent=4)
        
        print(f"Success [p03_marginals]: {self.dataset_name} -> {output_path}")
