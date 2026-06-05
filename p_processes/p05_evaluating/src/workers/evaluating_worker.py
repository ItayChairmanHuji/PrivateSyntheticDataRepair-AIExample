from dataclasses import dataclass
from typing import Any
from u_utilities.u_shared.pipeline_result import PipelineResult

@dataclass
class EvaluatingWorker:
    """Worker: Encapsulates the evaluation logic."""
    evaluator: Any # The hydra-instantiated evaluator (or orchestrator of evaluators)

    def evaluate(self, result: PipelineResult) -> dict:
        if hasattr(self.evaluator, "run"):
            return self.evaluator.run(result)
        return self.evaluator.evaluate(result)
