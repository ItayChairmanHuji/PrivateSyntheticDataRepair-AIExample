from dataclasses import dataclass
from .engine import MarginalSamplingEngine
from .core.sampling_core import MarginalSamplingCore

@dataclass
class MarginalSamplingWorker:
    """Orchestrator: Coordinates marginal sampling."""
    engine: MarginalSamplingEngine
    core: MarginalSamplingCore
    dataset_name: str
    noise_level: float
    sample_size: int

    def run(self):
        # 1. Load
        marginal_set = self.engine.load_marginals(self.dataset_name, self.noise_level)
        
        # 2. Sample
        sampled_set = self.core.sample(marginal_set)
        
        # 3. Save
        self.engine.save_sampled_marginals(
            sampled_set, 
            self.dataset_name, 
            self.noise_level, 
            self.sample_size
        )
        
        print(f"Success [p03b_marginal_sampling]: {self.dataset_name} (noise={self.noise_level}, sampled={self.sample_size})")
