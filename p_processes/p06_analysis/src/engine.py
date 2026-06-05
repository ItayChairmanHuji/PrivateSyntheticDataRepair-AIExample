from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager

@dataclass
class AnalysisEngine:
    """Engine: Handles resource interaction for the analysis process."""
    manager: ResourceManager

    def resolve_result_dir(self, experiment_id: str, timestamp: str = "latest") -> Path:
        return self.manager.resolver.resolve(
            "result", 
            experiment_id=experiment_id, 
            timestamp=timestamp
        )
        
    def resolve_analysis_dir(self, experiment_id: str) -> Path:
        return self.manager.resolver.resolve(
            "analysis", 
            experiment_id=experiment_id
        )
