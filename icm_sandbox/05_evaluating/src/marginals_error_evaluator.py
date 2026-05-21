from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class MarginalsErrorEvaluator(Evaluator):
    """
    Logs the average error of the obtained marginals for synthetic and repaired datasets.
    """
    def evaluate(self, result: PipelineResult) -> dict:
        marginals = result.obtained_marginals
        if not marginals or len(marginals) == 0:
            return {"marginals_error": {}}

        syn_errors = [m.calculate_error(result.synthetic_dataset.data) for m in marginals]
        rep_errors = [m.calculate_error(result.repaired_dataset.data) for m in marginals]
        
        return {
            "marginals_error": {
                "synthetic_avg": sum(syn_errors) / len(syn_errors),
                "repaired_avg": sum(rep_errors) / len(rep_errors)
            }
        }
