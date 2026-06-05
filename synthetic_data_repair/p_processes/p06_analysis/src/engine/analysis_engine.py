from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager

@dataclass
class AnalysisEngine:
    """Engine: Handles path resolution for the analysis process."""
    manager: ResourceManager

    def resolve_result_dir(self, experiment_id: str, timestamp: str = "latest") -> Path:
        return self.manager.resolver.get_result_dir(experiment_id, timestamp)
        
    def resolve_analysis_dir(self, experiment_id: str) -> Path:
        # Assuming ResourceManager has or could have a method for analysis output
        # For now, we put it in r_resources/r_analysis/...
        return Path(self.manager.resolver.root_dir) / "r_resources" / "r_analysis" / experiment_id
