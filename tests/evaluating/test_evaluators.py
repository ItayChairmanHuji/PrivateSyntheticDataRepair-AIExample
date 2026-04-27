import sys
import os
import pandas as pd
import unittest
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.evaluating.violation_evaluator import ViolationEvaluator
from src.evaluating.deletion_ratio_evaluator import DeletionRatioEvaluator
from src.evaluating.tvd_evaluator import TwoWayTVDEvaluator
from src.evaluating.runtime_evaluator import RuntimeEvaluator
from src.evaluating.marginals_error_evaluator import MarginalsErrorEvaluator
from src.entities.pipeline_result import PipelineResult
from src.entities.dataset import DatasetWithViolations
from src.entities.denial_constraints import DenialConstraints
from src.entities.marginal import Marginal, MarginalSet

class MockDataset(DatasetWithViolations):
    def __init__(self, name, data, dcs=None):
        super().__init__(name=name, data=data, dcs=dcs or DenialConstraints([]), target="")
    
    def get_violations(self):
        # Return a mock dataframe with some rows to simulate violations
        if "violate" in self.name:
            return pd.DataFrame({'idx1': [0], 'idx2': [1]})
        return pd.DataFrame(columns=['idx1', 'idx2'])

class TestEvaluators(unittest.TestCase):

    def setUp(self):
        self.p_data = pd.DataFrame({'A': [1, 1], 'B': [1, 2]})
        self.s_data = pd.DataFrame({'A': [1, 1, 1], 'B': [1, 2, 2]})
        self.r_data = pd.DataFrame({'A': [1, 1], 'B': [1, 2]})
        
        self.p_ds = MockDataset("private", self.p_data)
        self.s_ds = MockDataset("synthetic_violate", self.s_data)
        self.r_ds = MockDataset("repaired", self.r_data)
        
        self.marginals = MarginalSet([
            Marginal(attr1='A', attr2='B', value1=1, value2=1, target=0.5)
        ])
        
        self.result = PipelineResult(
            private_dataset=self.p_ds,
            synthetic_dataset=self.s_ds,
            repaired_dataset=self.r_ds,
            obtained_marginals=self.marginals,
            runtimes={"stage1": 1.0},
            metadata={"test": True}
        )

    def test_violation_evaluator(self):
        evaluator = ViolationEvaluator()
        metrics = evaluator.evaluate(self.result)
        self.assertEqual(metrics["violations"]["private"], 0)
        self.assertEqual(metrics["violations"]["synthetic"], 1)
        self.assertEqual(metrics["violations"]["repaired"], 0)

    def test_deletion_ratio_evaluator(self):
        evaluator = DeletionRatioEvaluator()
        metrics = evaluator.evaluate(self.result)
        # before=3, after=2. ratio = (3-2)/3 = 1/3
        self.assertAlmostEqual(metrics["deletion_ratio"]["ratio"], 1/3)

    def test_runtime_evaluator(self):
        evaluator = RuntimeEvaluator()
        metrics = evaluator.evaluate(self.result)
        self.assertEqual(metrics["runtimes"]["stage1"], 1.0)

    def test_tvd_evaluator(self):
        evaluator = TwoWayTVDEvaluator()
        metrics = evaluator.evaluate(self.result)
        
        # Calculation for P vs S:
        # P: (1,1)->0.5, (1,2)->0.5
        # S: (1,1)->1/3, (1,2)->2/3
        # TVD = 0.5 * (|0.5 - 1/3| + |0.5 - 2/3|) = 0.5 * (1/6 + 1/6) = 1/6
        self.assertAlmostEqual(metrics["tvd_2way"]["synthetic_avg"], 1/6)
        
        # Calculation for P vs R:
        # R matches P exactly
        # TVD = 0.0
        self.assertAlmostEqual(metrics["tvd_2way"]["repaired_avg"], 0.0)

    def test_marginals_error_evaluator(self):
        evaluator = MarginalsErrorEvaluator()
        metrics = evaluator.evaluate(self.result)
        # Marginal: A=1, B=1, target=0.5
        # Syn: (1,1) appears 1/3 times. Error = abs(1/3 - 0.5) / (1/3) = abs(-1/6) / (1/3) = 0.5
        # Rep: (1,1) appears 1/2 times. Error = abs(0.5 - 0.5) / 0.5 = 0
        self.assertAlmostEqual(metrics["marginals_error"]["synthetic_avg"], 0.5)
        self.assertAlmostEqual(metrics["marginals_error"]["repaired_avg"], 0.0)

if __name__ == "__main__":
    unittest.main()
