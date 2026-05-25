from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class ResultLoader:
    """Handles locating and loading experiment result files."""
    input_base_dir: Path = Path("remote/output")

    def get_input_path(self, experiment_name: str) -> Path:
        """Finds the aggregated summary CSV for the given experiment."""
        # Try local preprocessed summary first
        local_path = Path("s06_analysis/input") / f"{experiment_name}_summary.csv"
        if local_path.exists():
            return local_path

        # Fallback to remote output (raw pulled data)
        remote_path = self.input_base_dir / f"{experiment_name}_summary.csv"
        if remote_path.exists():
            return remote_path
            
        raise FileNotFoundError(f"Could not find summary for {experiment_name}. Checked: {remote_path}, {local_path}")
