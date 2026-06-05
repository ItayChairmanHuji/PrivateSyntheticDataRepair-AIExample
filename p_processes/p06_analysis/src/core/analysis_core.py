from dataclasses import dataclass
from typing import Any, List
from pathlib import Path

@dataclass
class AnalysisCore:
    """Logic: Encapsulates the analysis core."""
    analyzer: Any # The hydra-instantiated analyzer (e.g. aggregator or plotter)

    def analyze(self, results: List[dict], output_dir: Path):
        if hasattr(self.analyzer, "analyze"):
            self.analyzer.analyze(results, output_dir)
        else:
            print("No valid analyze method found on the analyzer.")
