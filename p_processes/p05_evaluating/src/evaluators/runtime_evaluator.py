﻿from old.s05_evaluating.src.components.evaluator import Evaluator
from u_utilities.u_shared.pipeline_result import PipelineResult

class RuntimeEvaluator(Evaluator):
    def evaluate(self, result: PipelineResult) -> dict:
        return {"runtimes": result.runtimes}

