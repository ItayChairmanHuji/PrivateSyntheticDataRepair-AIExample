import unittest
import pandas as pd
import numpy as np
from src.evaluating.ml_accuracy_evaluator import MLAccuracyEvaluator
from src.entities.pipeline_result import PipelineResult
from src.entities.dataset import Dataset
from src.entities.denial_constraints import DenialConstraints

class TestMLAccuracyEvaluator(unittest.TestCase):

    def setUp(self):
        # Create dummy data for classification
        # We need enough rows to split and have at least 2 classes
        data = pd.DataFrame({
            'feat1': np.random.randn(100),
            'feat2': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        self.p_ds = Dataset("private", data, DenialConstraints([]), "target")
        self.s_ds = Dataset("synthetic", data.copy(), DenialConstraints([]), "target")
        self.r_ds = Dataset("repaired", data.copy(), DenialConstraints([]), "target")
        
        self.result = PipelineResult(
            private_dataset=self.p_ds,
            synthetic_dataset=self.s_ds,
            repaired_dataset=self.r_ds,
            obtained_marginals=None,
            runtimes={},
            metadata={}
        )

    def test_evaluate_basic(self):
        evaluator = MLAccuracyEvaluator()
        metrics = evaluator.evaluate(self.result)
        
        self.assertIn("ml_accuracy", metrics)
        ma = metrics["ml_accuracy"]
        
        for key in ["private_gold_standard", "synthetic", "repaired"]:
            self.assertIn(key, ma)
            for model in ["logistic_regression", "random_forest", "mlp"]:
                self.assertIn(model, ma[key])
                self.assertIsInstance(ma[key][model], float)
                self.assertGreaterEqual(ma[key][model], 0.0)
                self.assertLessEqual(ma[key][model], 1.0)

    def test_missing_target(self):
        self.p_ds.target = "wrong_target"
        evaluator = MLAccuracyEvaluator()
        metrics = evaluator.evaluate(self.result)
        self.assertEqual(metrics, {"ml_accuracy": {}})

    def test_single_class(self):
        # Test case where training data has only one class
        self.s_ds.data['target'] = 1
        evaluator = MLAccuracyEvaluator()
        metrics = evaluator.evaluate(self.result)
        
        # Synthetic should have accuracy corresponding to majority baseline
        ma = metrics["ml_accuracy"]["synthetic"]
        self.assertIn("mlp", ma)
        # Since p_test has ~50/50 split, accuracy should be around 0.5
        self.assertAlmostEqual(ma["mlp"], (self.result.private_dataset.data['target'] == 1).mean(), delta=0.2)

if __name__ == "__main__":
    unittest.main()
