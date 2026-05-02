import time
from dataclasses import dataclass
from src.loading.loader import Loader
from src.synthesizing.synthesizer import Synthesizer
from src.marginals_obtaining.obtainer import Obtainer
from src.repairing.repairer import Repairer
from src.evaluating.evaluation_orchestrator import EvaluationOrchestrator
from src.entities.pipeline_result import PipelineResult

@dataclass
class Pipeline:
    """
    The main orchestrator that runs the full research experiment pipeline.
    """
    loader: Loader
    synthesizer: Synthesizer
    obtainer: Obtainer
    repairer: Repairer
    evaluator: EvaluationOrchestrator

    def run(self) -> dict:
        runtimes = {}

        # 1. Loading
        print(f"--- Stage 1: Loading ---")
        start = time.time()
        private_dataset = self.loader.load()
        runtimes['loading'] = time.time() - start

        # 2. Synthesizing
        print(f"--- Stage 2: Synthesizing ---")
        start = time.time()
        synthetic_dataset = self.synthesizer.synthesize(private_dataset)
        runtimes['synthesizing'] = time.time() - start

        # 3. Marginals Obtaining
        print(f"--- Stage 3: Marginals Obtaining ---")
        start = time.time()
        obtained_marginals = self.obtainer.obtain(private_dataset, synthetic_dataset)
        runtimes['marginals_obtaining'] = time.time() - start

        # 4. Repairing
        print(f"--- Stage 4: Repairing ---")
        start = time.time()
        
        # Repairing in a single pass as repairers are designed to handle all identified conflicts.
        repaired_dataset = self.repairer.repair(synthetic_dataset, obtained_marginals)
        
        # Final sanity check for research logging
        remaining_v = len(repaired_dataset.get_violations())
        if remaining_v == 0:
            print("Repair complete: All violations removed.")
        else:
            print(f"Warning: Repair complete but {remaining_v} violations remain.")
            
        runtimes['repairing'] = time.time() - start

        # 5. Evaluating
        print(f"--- Stage 5: Evaluating ---")
        
        from src.utils.serialization_helper import get_serializable_params
        
        metadata = {
            "loader": self.loader.__class__.__name__,
            "synthesizer": self.synthesizer.__class__.__name__,
            "obtainer": self.obtainer.__class__.__name__,
            "repairer": self.repairer.__class__.__name__,
            "synthesizer_params": get_serializable_params(self.synthesizer),
            "obtainer_params": get_serializable_params(self.obtainer),
            "repairer_params": get_serializable_params(self.repairer)
        }

        pipeline_result = PipelineResult(
            private_dataset=private_dataset,
            synthetic_dataset=synthetic_dataset,
            repaired_dataset=repaired_dataset,
            obtained_marginals=obtained_marginals,
            runtimes=runtimes,
            metadata=metadata
        )
        
        # The evaluator orchestrator handles saving to JSON
        final_metrics = self.evaluator.run(pipeline_result)
        
        print("--- Pipeline Complete ---")
        return final_metrics
