from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager, DataMode

@dataclass
class SamplingEngine:
    """Engine: Handles resource interaction for the sampling process."""
    manager: ResourceManager

    def resolve_model_path(self, dataset_name: str, engine_name: str, epsilon: float, seed: int) -> Path:
        return self.manager.resolver.resolve(
            "model",
            dataset_name=dataset_name,
            synth_name=engine_name,
            epsilon=epsilon,
            seed=seed
        )

    def resolve_synthetic_data_path(self, dataset_name: str, engine_name: str, epsilon: float, seed: int, size: int) -> Path:
        return self.manager.resolver.resolve(
            "data",
            name=dataset_name,
            synth_name=engine_name,
            epsilon=epsilon,
            seed=seed,
            size=size,
            mode=DataMode.SYNTHETIC
        )
