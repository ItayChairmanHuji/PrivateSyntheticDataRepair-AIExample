import json
from dataclasses import dataclass
import pandas as pd
from u_utilities.u_shared import Dataset
from u_utilities.u_shared.pipeline_result import PipelineResult

from ..engine.evaluating_engine import EvaluatingEngine
from ..workers.evaluating_worker import EvaluatingWorker

@dataclass
class EvaluatingOrchestrator:
    """Facade: Orchestrates the end-to-end evaluating process."""
    engine: EvaluatingEngine
    worker: EvaluatingWorker
    dataset_name: str
    synthesizer_name: str
    repairer_name: str
    epsilon: float
    seed: int
    size: int
    alpha: float
    experiment_id: str
    timestamp: str = "latest"

    def run(self):
        """Executes the evaluating flow."""
        private_dataset = self.engine.manager.load_dataset(self.dataset_name)
        
        synth_path = self.engine.resolve_synthetic_data_path(
            self.dataset_name, self.synthesizer_name, self.epsilon, self.seed, self.size
        )
        synth_df = pd.read_csv(synth_path) if synth_path.exists() else pd.DataFrame()
        synthetic_dataset = Dataset(
            name=f"{self.dataset_name}_syn",
            data=synth_df,
            dcs=private_dataset.dcs,
            target=private_dataset.target,
            mappings=private_dataset.mappings
        )
        
        repaired_path = self.engine.resolve_repaired_data_path(
            self.dataset_name, self.repairer_name, self.synthesizer_name, 
            self.epsilon, self.seed, self.size, self.alpha
        )
        repaired_df = pd.read_csv(repaired_path) if repaired_path.exists() else pd.DataFrame()
        repaired_dataset = Dataset(
            name=f"{self.dataset_name}_rep",
            data=repaired_df,
            dcs=private_dataset.dcs,
            target=private_dataset.target,
            mappings=private_dataset.mappings
        )
        
        # In a full flow we'd also load marginals and runtimes here
        pipeline_result = PipelineResult(
            private_dataset=private_dataset,
            synthetic_dataset=synthetic_dataset,
            repaired_dataset=repaired_dataset,
            obtained_marginals=[],
            runtimes={},
            metadata={"alpha": self.alpha, "epsilon": self.epsilon}
        )
        
        results = self.worker.evaluate(pipeline_result)
        
        output_dir = self.engine.resolve_result_dir(self.experiment_id, self.timestamp)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"result_{self.dataset_name}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        
        print(f"Success [p05_evaluating]: Results saved -> {output_file}")
