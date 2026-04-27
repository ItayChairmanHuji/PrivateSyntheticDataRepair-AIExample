import sys
import os
import pandas as pd
import unittest
import json
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.evaluating.evaluation_orchestrator import EvaluationOrchestrator
from src.evaluating.violation_evaluator import ViolationEvaluator
from src.evaluating.runtime_evaluator import RuntimeEvaluator
from src.entities.pipeline_result import PipelineResult
from src.entities.dataset import DatasetWithViolations
from src.entities.denial_constraints import DenialConstraints

class MockDataset(DatasetWithViolations):
    def __init__(self, name, data):
        super().__init__(name=name, data=data, dcs=DenialConstraints([]), target="")
    def get_violations(self):
        return pd.DataFrame(columns=['idx1', 'idx2'])

class TestOrchestrator(unittest.TestCase):

    def setUp(self):
        self.test_results_dir = Path("temp_test_results")
        self.orchestrator = EvaluationOrchestrator(
            evaluators=[ViolationEvaluator(), RuntimeEvaluator()],
            output_dir=str(self.test_results_dir),
            experiment_name="test_experiment"
        )
        
        ds = MockDataset("dummy", pd.DataFrame({'A': [1]}))
        self.result = PipelineResult(
            private_dataset=ds,
            synthetic_dataset=ds,
            repaired_dataset=ds,
            obtained_marginals=None,
            runtimes={"total": 5.0}
        )

    def tearDown(self):
        if self.test_results_dir.exists():
            shutil.rmtree(self.test_results_dir)

    def test_orchestration_and_saving(self):
        full_results = self.orchestrator.run(self.result)
        
        # Check if metrics are combined
        self.assertIn("violations", full_results)
        self.assertIn("runtimes", full_results)
        self.assertEqual(full_results["dataset_name"], "dummy")
        
        # Check if file is saved
        target_path = self.test_results_dir / "test_experiment"
        self.assertTrue(target_path.exists())
        
        files = list(target_path.glob("result_dummy_*.json"))
        self.assertEqual(len(files), 1)
        
        with open(files[0], "r") as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data["violations"]["private"], 0)
            self.assertEqual(saved_data["runtimes"]["total"], 5.0)

if __name__ == "__main__":
    unittest.main()
