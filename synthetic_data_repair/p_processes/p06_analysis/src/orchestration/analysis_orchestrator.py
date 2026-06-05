import json
from dataclasses import dataclass
from pathlib import Path
from ..engine.analysis_engine import AnalysisEngine
from ..workers.analysis_worker import AnalysisWorker

@dataclass
class AnalysisOrchestrator:
    """Facade: Orchestrates the end-to-end analysis process."""
    engine: AnalysisEngine
    worker: AnalysisWorker
    experiment_id: str
    timestamp: str = "latest"

    def run(self):
        """Executes the analysis flow."""
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
        
        # Prepare output directory
        analysis_dir = self.engine.resolve_analysis_dir(self.experiment_id)
        analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Analyze
        self.worker.analyze(results, analysis_dir)
        
        print(f"Success [p06_analysis]: Analysis saved -> {analysis_dir}")
