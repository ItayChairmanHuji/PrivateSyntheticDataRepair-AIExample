import json
from dataclasses import dataclass
import pandas as pd
from u_utilities.u_shared import Dataset
from u_utilities.u_shared.marginal import MarginalSet

from ..engine.repairing_engine import RepairingEngine
from ..workers.repairing_worker import RepairingWorker

@dataclass
class RepairingOrchestrator:
    """Facade: Orchestrates the end-to-end repairing process."""
    engine: RepairingEngine
    worker: RepairingWorker
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
        # Load synthetic data
        synth_path = self.engine.resolve_synthetic_data_path(
            self.dataset_name, self.synthesizer_name, self.epsilon, self.seed, self.size
        )
        # Note: In a real scenario we'd use ResourceManager for Dataset loading,
        # but here we'll mock the dataset construction if manager lacks a specific synthetic loader.
        # Assuming we need to load constraints & metadata from private data, then synthetic CSV.
        private_dataset = self.engine.manager.load_dataset(self.dataset_name)
        synth_df = pd.read_csv(synth_path)
        
        synthetic_dataset = Dataset(
            name=f"{self.dataset_name}_syn",
            data=synth_df,
            dcs=private_dataset.dcs,
            target=private_dataset.target,
            mappings=private_dataset.mappings
        )
        
        # Load marginals
        marginal_path = self.engine.resolve_marginal_path(self.dataset_name, self.noise_level)
        with open(marginal_path, "r") as f:
            marginals_data = json.load(f)
            marginals = MarginalSet.from_dict(marginals_data)
        
        # Repair
        repaired_dataset = self.worker.repair(synthetic_dataset, marginals)
        
        # Save output
        output_path = self.engine.resolve_repaired_data_path(
            self.dataset_name, self.repairer_name, self.synthesizer_name, 
            self.epsilon, self.seed, self.size, self.alpha
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        repaired_dataset.data.to_csv(output_path, index=False)
        
        print(f"Success [p04_repairing]: Repaired data saved -> {output_path}")
