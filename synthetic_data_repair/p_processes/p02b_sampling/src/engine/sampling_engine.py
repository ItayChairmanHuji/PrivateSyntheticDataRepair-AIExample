from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager

@dataclass
class SamplingEngine:
    """Engine: Handles path resolution for the sampling process."""
    manager: ResourceManager

    def resolve_model_path(self, dataset_name: str, engine_name: str, epsilon: float, seed: int) -> Path:
        return self.manager.get_model_path(dataset_name, engine_name, epsilon, seed)

    def resolve_synthetic_data_path(self, dataset_name: str, engine_name: str, epsilon: float, seed: int, size: int) -> Path:
        return self.manager.get_synthetic_data_path(dataset_name, engine_name, epsilon, seed, size)
