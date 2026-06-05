﻿
from old.s05_evaluating.src.components.evaluator import Evaluator
from u_utilities.u_shared.pipeline_result import PipelineResult

class ViolationEvaluator(Evaluator):
    """
    Evaluates the number of violations in private, synthetic and repaired datasets.
    """
    def evaluate(self, result: PipelineResult) -> dict:
        return {
            "violations": {
                "private": len(result.private_dataset.get_violations()),
                "synthetic": len(result.synthetic_dataset.get_violations()),
                "repaired": len(result.repaired_dataset.get_violations())
            }
        }

