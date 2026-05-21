from s05_evaluating.src.components.evaluator import Evaluator
from shared.entities.pipeline_result import PipelineResult

class RuntimeEvaluator(Evaluator):
    def evaluate(self, result: PipelineResult) -> dict:
        return {"runtimes": result.runtimes}

