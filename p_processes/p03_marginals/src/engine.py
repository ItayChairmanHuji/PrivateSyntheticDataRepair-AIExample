from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager

@dataclass
class MarginalsEngine:
    """Engine: Handles resource interaction for the marginals process."""
    manager: ResourceManager

    def load_dataset(self, dataset_name: str):
        return self.manager.load_dataset(dataset_name)

    def save_marginals(self, marginals, dataset_name: str, noise_level: float):
        self.manager.save_marginals(
            marginals, 
            dataset_name=dataset_name, 
            noise_level=noise_level
        )
