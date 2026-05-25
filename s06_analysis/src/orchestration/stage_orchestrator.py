from dataclasses import dataclass
from pathlib import Path
from typing import Any
import pandas as pd

@dataclass
class StageOrchestrator:
    """Orchestrates the analysis stage: loading, flattening results and generating notebooks."""
    loader: Any
    generator: Any
    flattener: Any
    output_dir: Path

    def run(self, experiment_name: str) -> Path:
        """Executes the analysis orchestration."""
        # 1. Load the results
        input_path = self.loader.get_input_path(experiment_name)
        df = pd.read_csv(input_path)
        
        # 2. Flatten/Clean the results
        df_flat, df_topology = self.flattener.flatten(df)
        
        # 3. Save artifacts for the notebook
        flat_path = Path("s06_analysis/input") / f"{experiment_name}_flat.csv"
        topo_path = Path("s06_analysis/input") / f"{experiment_name}_topology.csv"
        
        flat_path.parent.mkdir(parents=True, exist_ok=True)
        df_flat.to_csv(flat_path, index=False)
        df_topology.to_csv(topo_path, index=False)
        
        # 4. Generate the notebook using the flattened paths
        notebook_path = self.generator.generate(
            experiment_name=experiment_name,
            input_path=flat_path,
            topology_path=topo_path,
            output_dir=self.output_dir
        )
        
        return notebook_path
