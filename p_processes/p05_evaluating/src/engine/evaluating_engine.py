from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager

@dataclass
class EvaluatingEngine:
    """Engine: Handles path resolution for the evaluating process."""
    manager: ResourceManager

    def resolve_synthetic_data_path(self, dataset_name: str, synthesizer_name: str, epsilon: float, seed: int, size: int) -> Path:
        return self.manager.get_synthetic_data_path(dataset_name, synthesizer_name, epsilon, seed, size)

    def resolve_repaired_data_path(self, dataset_name: str, repairer_name: str, synthesizer_name: str, epsilon: float, seed: int, size: int, alpha: float) -> Path:
        return self.manager.get_repaired_data_path(dataset_name, repairer_name, synthesizer_name, epsilon, seed, size, alpha)

    def resolve_result_dir(self, experiment_id: str, timestamp: str) -> Path:
        return self.manager.resolver.get_result_dir(experiment_id, timestamp)
