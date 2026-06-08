from typing import Any
import json
from dataclasses import dataclass
import pandas as pd
from u_utilities.u_shared import Dataset, PipelineResult

from .engine import EvaluatingEngine
from .core.evaluating_core import EvaluatingCore

@dataclass
class EvaluatingWorker:
    """Orchestrator: Coordinates the Engine and Logic for the evaluating process."""
    engine: EvaluatingEngine
    core: EvaluatingCore
    dataset_name: str
    synthesizer_name: str
    repairer_name: str
    epsilon: float
    seed: int
    size: int
    alpha: float
    noise_level: Any
    experiment_id: str
    timestamp: str = "latest"

    def run(self):
        """Executes the evaluating flow."""
        # 1. Use Engine to load the private resource
        private_dataset = self.engine.manager.load_dataset(self.dataset_name)
        
        # 2. Use Engine to resolve synthetic/repaired paths
        synth_path = self.engine.resolve_synthetic_data_path(
            self.dataset_name, self.synthesizer_name, self.epsilon, self.seed, self.size
        )
        if not synth_path.exists():
            raise FileNotFoundError(f"Synthetic data not found: {synth_path}")
        synth_df = pd.read_csv(synth_path)
        synthetic_dataset = Dataset(
            name=f"{self.dataset_name}_syn",
            data=synth_df,
            dcs=private_dataset.dcs,
            target=private_dataset.target,
            mappings=private_dataset.mappings
        )
        
        repaired_path = self.engine.resolve_repaired_data_path(
            self.dataset_name, self.repairer_name, self.synthesizer_name, 
            self.epsilon, self.seed, self.size, self.noise_level, self.alpha
        )
        if not repaired_path.exists():
            raise FileNotFoundError(f"Repaired data not found: {repaired_path}")
        repaired_df = pd.read_csv(repaired_path)
        repaired_dataset = Dataset(
            name=f"{self.dataset_name}_rep",
            data=repaired_df,
            dcs=private_dataset.dcs,
            target=private_dataset.target,
            mappings=private_dataset.mappings
        )
        
        # Prepare pipeline result
        pipeline_result = PipelineResult(
            private_dataset=private_dataset,
            synthetic_dataset=synthetic_dataset,
            repaired_dataset=repaired_dataset,
            obtained_marginals=[],
            runtimes={},
            metadata={"alpha": self.alpha, "epsilon": self.epsilon}
        )
        
        output_dir = self.engine.resolve_result_dir(self.experiment_id, self.timestamp)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / self._result_filename()
        if output_file.exists():
            print(f"Skipping [p05_evaluating]: {output_file} already exists.")
            return

        # 3. Use Logic to perform the evaluation
        results = self.core.evaluate(pipeline_result)

        # 4. Save the parameterized result file
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        
        print(f"Success [p05_evaluating]: Results saved -> {output_file}")

    def _result_filename(self) -> str:
        parts = [
            "result",
            self.dataset_name,
            self.synthesizer_name,
            self.repairer_name,
            str(self.epsilon),
            str(self.seed),
            str(self.size),
            str(self.noise_level),
            str(self.alpha),
        ]
        safe_parts = [part.replace("/", "_").replace("\\", "_") for part in parts]
        return "_".join(safe_parts) + ".json"
