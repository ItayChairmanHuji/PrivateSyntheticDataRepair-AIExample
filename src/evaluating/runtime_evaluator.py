from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class RuntimeEvaluator(Evaluator):
    def evaluate(self, result: PipelineResult) -> dict:
        return {"runtimes": result.runtimes}
