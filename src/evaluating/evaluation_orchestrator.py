import json
import os
import uuid
from datetime import datetime
from typing import List

from src.entities.pipeline_result import PipelineResult
from src.evaluating.evaluator import Evaluator


class EvaluationOrchestrator:
    def __init__(
        self,
        evaluators: List[Evaluator],
        output_dir: str = "results",
        experiment_name: str = None,
    ):
        self.evaluators = evaluators
        self.output_dir = output_dir
        self.experiment_name = experiment_name

        target_dir = self.output_dir
        if self.experiment_name:
            target_dir = os.path.join(self.output_dir, self.experiment_name)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        self.target_dir = target_dir

    def run(self, result: PipelineResult) -> dict:
        full_results = self._run_evaluators(result)
        self._write_metadata(full_results, result)
        self._save_results(result, full_results)
        return full_results

    def _run_evaluators(self, result: PipelineResult) -> dict:
        full_results = {}
        for evaluator in self.evaluators:
            try:
                eval_result = evaluator.evaluate(result)
                full_results.update(eval_result)
            except Exception as e:
                print(f"Error in evaluator {evaluator.__class__.__name__}: {e}")
        return full_results

    def _write_metadata(self, full_results, result: PipelineResult):
        full_results["dataset_name"] = result.private_dataset.name
        full_results["timestamp"] = datetime.now().isoformat()
        full_results["experiment_id"] = str(uuid.uuid4())[:8]
        if self.experiment_name:
            full_results["experiment_name"] = self.experiment_name
        if result.metadata:
            full_results["metadata"] = result.metadata

    def _save_results(self, result: PipelineResult, full_results: dict):
        filename = (
            f"result_{result.private_dataset.name}_{full_results['experiment_id']}.json"
        )
        filepath = os.path.join(self.target_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(full_results, f, indent=4)
        print(f"Results saved to {filepath}")
