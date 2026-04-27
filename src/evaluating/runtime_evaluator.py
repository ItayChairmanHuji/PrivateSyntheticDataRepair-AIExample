from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class RuntimeEvaluator(Evaluator):
    """
    Logs the runtime of each part of the pipeline.
    """
    def evaluate(self, result: PipelineResult) -> dict:
        return {"runtimes": result.runtimes}
