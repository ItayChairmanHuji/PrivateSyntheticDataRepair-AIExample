import json
from dataclasses import dataclass
import pandas as pd
from u_utilities.u_shared import Dataset, MarginalSet

from .engine import RepairingEngine
from .core.repairing_core import RepairingCore

@dataclass
class RepairingWorker:
    """Orchestrator: Coordinates the Engine and Logic for the repairing process."""
    engine: RepairingEngine
    core: RepairingCore
    dataset_name: str
    synthesizer_name: str
    repairer_name: str
    epsilon: float
    seed: int
    size: int
    noise_level: float
    alpha: float

    def run(self):
        """Executes the repairing flow."""
        # 1. Use the Engine to resolve paths
        synth_path = self.engine.resolve_synthetic_data_path(
            self.dataset_name, self.synthesizer_name, self.epsilon, self.seed, self.size
        )
        
        # Load constraints & metadata from private data
        private_dataset = self.engine.manager.load_dataset(self.dataset_name)
        synth_df = pd.read_csv(synth_path)
        
        synthetic_dataset = Dataset(
            name=f"{self.dataset_name}_syn",
            data=synth_df,
            dcs=private_dataset.dcs,
            target=private_dataset.target,
            mappings=private_dataset.mappings
        )
        
        # Load marginals via Engine resolution
        marginal_path = self.engine.resolve_marginal_path(self.dataset_name, self.noise_level)
        with open(marginal_path, "r") as f:
            marginals_data = json.load(f)
            marginals = MarginalSet.from_dict(marginals_data)
        
        # 2. Use Logic to perform the repair
        repaired_dataset = self.core.repair(synthetic_dataset, marginals)
        
        # 3. Use the Engine to resolve output path and save
        output_path = self.engine.resolve_repaired_data_path(
            self.dataset_name, self.repairer_name, self.synthesizer_name, 
            self.epsilon, self.seed, self.size, self.alpha
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        repaired_dataset.data.to_csv(output_path, index=False)
        
        print(f"Success [p04_repairing]: Repaired data saved -> {output_path}")
