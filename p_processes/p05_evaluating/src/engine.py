from dataclasses import dataclass
from pathlib import Path
from typing import Any
from u_utilities.u_io import ResourceManager, DataMode

@dataclass
class EvaluatingEngine:
    """Engine: Handles resource interaction for the evaluating process."""
    manager: ResourceManager

    def resolve_synthetic_data_path(self, dataset_name: str, synthesizer_name: str, epsilon: float, seed: int, size: int) -> Path:
        return self.manager.resolver.resolve(
            "data", 
            name=dataset_name, 
            mode=DataMode.SYNTHETIC,
            synth_name=synthesizer_name,
            epsilon=epsilon,
            seed=seed,
            size=size
        )

    def resolve_repaired_data_path(self, dataset_name: str, repairer_name: str, synthesizer_name: str, epsilon: float, seed: int, size: int, noise: Any, alpha: float) -> Path:
        return self.manager.resolver.resolve(
            "data",
            name=dataset_name,
            mode=DataMode.REPAIRED,
            repairer_name=repairer_name,
            synth_name=synthesizer_name,
            epsilon=epsilon,
            seed=seed,
            size=size,
            noise_level=noise,
            alpha=alpha
        )

    def resolve_result_dir(self, experiment_id: str, timestamp: str) -> Path:
        return self.manager.resolver.resolve(
            "result",
            experiment_id=experiment_id,
            timestamp=timestamp
        )
