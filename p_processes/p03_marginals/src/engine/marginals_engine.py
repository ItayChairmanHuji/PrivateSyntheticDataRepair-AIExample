from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager

@dataclass
class MarginalsEngine:
    """Engine: Handles path resolution for the marginals process."""
    manager: ResourceManager

    def resolve_marginal_path(self, dataset_name: str, noise_level: float) -> Path:
        return self.manager.get_marginal_path(dataset_name, noise_level)
