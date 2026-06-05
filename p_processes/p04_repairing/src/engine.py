from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager, DataMode

@dataclass
class RepairingEngine:
    """Engine: Handles resource interaction for the repairing process."""
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

    def resolve_marginal_path(self, dataset_name: str, noise_level: float) -> Path:
        return self.manager.resolver.resolve(
            "marginal", 
            dataset_name=dataset_name, 
            noise_level=noise_level
        )

    def resolve_repaired_data_path(self, dataset_name: str, repairer_name: str, synthesizer_name: str, epsilon: float, seed: int, size: int, alpha: float) -> Path:
        return self.manager.resolver.resolve(
            "data",
            name=dataset_name,
            mode=DataMode.REPAIRED,
            repairer_name=repairer_name,
            synth_name=synthesizer_name,
            epsilon=epsilon,
            seed=seed,
            size=size,
            alpha=alpha
        )
