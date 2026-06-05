import json
from dataclasses import dataclass
from .engine import AnalysisEngine
from .core.analysis_core import AnalysisCore

@dataclass
class AnalysisWorker:
    """Orchestrator: Coordinates the Engine and Logic for the analysis process."""
    engine: AnalysisEngine
    core: AnalysisCore
    experiment_id: str
    timestamp: str = "latest"

    def run(self):
        """Executes the analysis flow."""
        # 1. Use the Engine to resolve where results are
        results_dir = self.engine.resolve_result_dir(self.experiment_id, self.timestamp)
        
        # Load all results
        results = []
        if results_dir.exists():
            for file_path in results_dir.glob("*.json"):
                try:
                    with open(file_path, "r") as f:
                        results.append(json.load(f))
                except Exception as e:
                    print(f"Failed to read result {file_path}: {e}")
        
        # 2. Use the Engine to resolve where to save analysis
        analysis_dir = self.engine.resolve_analysis_dir(self.experiment_id)
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Use Logic to perform the analysis
        self.core.analyze(results, analysis_dir)
        
        print(f"Success [p06_analysis]: Analysis saved -> {analysis_dir}")
