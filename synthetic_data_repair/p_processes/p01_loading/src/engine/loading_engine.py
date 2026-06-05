from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager

@dataclass
class LoadingEngine:
    """Engine: Handles path resolution for the loading process."""
    manager: ResourceManager

    def resolve_output_dir(self, dataset_name: str) -> Path:
        """Resolves the physical directory for private dataset storage."""
        return self.manager.resolver.get_private_data_dir(dataset_name)
