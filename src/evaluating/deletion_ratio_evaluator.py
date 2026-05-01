from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class DeletionRatioEvaluator(Evaluator):
    def evaluate(self, result: PipelineResult) -> dict:
        n_before = len(result.synthetic_dataset.data)
        n_after = len(result.repaired_dataset.data)
        
        ratio = (n_before - n_after) / n_before if n_before > 0 else 0.0
        return {
            "deletion_ratio": {
                "before": n_before,
                "after": n_after,
                "ratio": ratio
            }
        }
