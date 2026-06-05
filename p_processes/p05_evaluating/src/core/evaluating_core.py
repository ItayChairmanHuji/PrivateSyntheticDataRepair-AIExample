from dataclasses import dataclass
from typing import Any
from u_utilities.u_shared import PipelineResult

@dataclass
class EvaluatingCore:
    """Logic: Encapsulates the evaluation core."""
    evaluator: Any # The hydra-instantiated evaluator (or worker of evaluators)

    def evaluate(self, result: PipelineResult) -> dict:
        if hasattr(self.evaluator, "run"):
            return self.evaluator.run(result)
        return self.evaluator.evaluate(result)
