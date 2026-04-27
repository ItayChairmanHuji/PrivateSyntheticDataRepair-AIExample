
from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class ViolationEvaluator(Evaluator):
    """
    Evaluates the number of violations in private, synthetic and repaired datasets.
    """
    def evaluate(self, result: PipelineResult) -> dict:
        return {
            "violations": {
                "private": len(result.private_dataset.violations),
                "synthetic": len(result.synthetic_dataset.violations),
                "repaired": len(result.repaired_dataset.violations)
            }
        }
