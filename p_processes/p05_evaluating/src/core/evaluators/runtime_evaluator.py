from p_processes.p05_evaluating.src.core.evaluators.evaluator import Evaluator
from u_utilities.u_shared import PipelineResult

class RuntimeEvaluator(Evaluator):
    def evaluate(self, result: PipelineResult) -> dict:
        return {"runtimes": result.runtimes}

