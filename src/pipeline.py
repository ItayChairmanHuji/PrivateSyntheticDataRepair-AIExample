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
        
        # Iterative repair to ensure all violations are removed (since finder might have limits)
        current_to_repair = synthetic_dataset
        max_repair_iterations = 5
        for i in range(max_repair_iterations):
            repaired_dataset = self.repairer.repair(current_to_repair, obtained_marginals)
            
            # Check for remaining violations (no limit here to be sure)
            remaining_violations = repaired_dataset.get_violations()
            if len(remaining_violations) == 0:
                print(f"Clean after {i+1} repair iteration(s).")
                break
            
            print(f"Iteration {i+1}: {len(remaining_violations)} violations remain. Retrying repair...")
            current_to_repair = repaired_dataset
        else:
            print(f"Warning: Repair did not converge after {max_repair_iterations} iterations.")
            
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
