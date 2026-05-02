import sys
import os
import pandas as pd
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.loading.violation_finder import ViolationFinder
from src.loading.components.dcs_loader import DCsLoader

class TestViolationFinder(unittest.TestCase):

    def setUp(self):
        self.finder = ViolationFinder()
        self.dcs_loader = DCsLoader()
        self.temp_dir = Path("temp_test_violations")
        self.temp_dir.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _get_dcs(self, content):
        path = self.temp_dir / "dcs.txt"
        path.write_text(content)
        return self.dcs_loader.load(path)

    def test_constant_implication(self):
        # Pattern 1: Unary/Constant (Pandas path)
        df = pd.DataFrame({'A': [1, 1, 2], 'B': [10, 20, 10]})
        # not(t1.A=1 & t1.B>15) -> Only Row 1 violates
        dcs = self._get_dcs("not(t1.A=1 & t1.B>15)")
        violations = self.finder.find_violations(df, dcs)
        
        # Result should contain pairs involving the violating row (Row 1).
        # Since we ignore self-conflicts (1,1), and we normalize to idx1 < idx2:
        # (1,0) -> (0,1)
        # (1,2) -> (1,2)
        
        self.assertEqual(len(violations), 2)
        actual_pairs = set(zip(violations['idx1'], violations['idx2']))
        self.assertEqual(actual_pairs, {(0, 1), (1, 2)})

    def test_functional_dependency(self):
        # Pattern 2: FD-like (Value-Partitioned Join)
        # not(t1.A=t2.A & t1.B!=t2.B)
        df = pd.DataFrame({'A': [1, 1, 2, 1], 'B': [10, 20, 10, 10]})
        dcs = self._get_dcs("not(t1.A=t2.A & t1.B!=t2.B)")
        violations = self.finder.find_violations(df, dcs)
        
        # Violating pairs (idx1 < idx2):
        # (0, 1): A=1, A=1 (equal) & B=10, B=20 (not equal) -> VIOLATION
        # (1, 3): A=1, A=1 (equal) & B=20, B=10 (not equal) -> VIOLATION
        # (0, 3): A=1, A=1 (equal) & B=10, B=10 (equal) -> SATISFIED
        
        expected_pairs = {(0, 1), (1, 3)}
        actual_pairs = set(zip(violations['idx1'], violations['idx2']))
        self.assertEqual(actual_pairs, expected_pairs)

    def test_order_constraints_asymmetric(self):
        # Pattern 3: Order (DuckDB path)
        # not(t1.Age < t2.Age & t1.Salary > t2.Salary)
        df = pd.DataFrame({
            'Age':    [20,   30,   25], 
            'Salary': [5000, 4000, 4500]
        })
        dcs = self._get_dcs("not(t1.Age < t2.Age & t1.Salary > t2.Salary)")
        violations = self.finder.find_violations(df, dcs)
        
        # Row 0: (20, 5000)
        # Row 1: (30, 4000)
        # Row 2: (25, 4500)
        
        # Pairs (idx1, idx2) with idx1 < idx2:
        # (0, 1): t1=0, t2=1 -> 20 < 30 (T) & 5000 > 4000 (T) -> VIOLATION
        # (0, 2): t1=0, t2=2 -> 20 < 25 (T) & 5000 > 4500 (T) -> VIOLATION
        # (1, 2): t1=1, t2=2 -> 30 < 25 (F) ... -> SATISFIED
        # (1, 2): t1=2, t2=1 -> 25 < 30 (T) & 4500 > 4000 (T) -> VIOLATION (This is pair {1, 2})
        
        # If the finder correctly identifies that the pair {1, 2} violates the DC 
        # (even if t1 must be 2 and t2 must be 1 to trigger the predicates), 
        # it should return (1, 2).
        
        expected_pairs = {(0, 1), (0, 2), (1, 2)}
        actual_pairs = set(zip(violations['idx1'], violations['idx2']))
        
        self.assertEqual(actual_pairs, expected_pairs, f"Expected {expected_pairs}, but got {actual_pairs}")

    def test_empty_results(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        dcs = self._get_dcs("not(t1.A=4)")
        violations = self.finder.find_violations(df, dcs)
        self.assertEqual(len(violations), 0)

if __name__ == "__main__":
    unittest.main()
