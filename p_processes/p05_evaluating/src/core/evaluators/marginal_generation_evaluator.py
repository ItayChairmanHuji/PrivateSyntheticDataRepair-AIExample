import numpy as np
from p_processes.p05_evaluating.src.core.evaluators.evaluator import Evaluator
from u_utilities.u_shared import PipelineResult

class MarginalGenerationEvaluator(Evaluator):
    """
    Evaluates the generation quality of the obtained marginals.
    Measures the average relative error between the noisy target and the true frequency in private data.
    """
    def evaluate(self, result: PipelineResult) -> dict:
        marginals = result.obtained_marginals
        if not marginals or len(marginals) == 0:
            return {"marginal_generation_quality": {}}

        private_data = result.private_dataset.data
        relative_errors = []
        
        for m in marginals:
            true_freq = m.calculate_frequency(private_data)
            # Avoid division by zero
            if true_freq > 0:
                rel_error = abs(m.target - true_freq) / true_freq
            else:
                rel_error = abs(m.target - true_freq)
            relative_errors.append(rel_error)
            
        return {
            "marginal_generation_quality": {
                "avg_relative_error": float(np.mean(relative_errors))
            }
        }

