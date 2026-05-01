import sys
import os
import pandas as pd
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.repairing.ilp_repairer import ILPRepairer
from src.entities.dataset import Dataset
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side
from src.entities.marginal import Marginal, MarginalSet

class TestILPRepairer(unittest.TestCase):

    def setUp(self):
        # Conflict: Row 0 and Row 1
        self.data = pd.DataFrame({
            'A': [1, 1, 2],
            'B': [10, 20, 10]
        })
        p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
        p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
        self.dcs = DenialConstraints([DenialConstraint([p1, p2])])
        self.ds = Dataset("dummy", self.data, self.dcs, "")
        
        # Marginal: want A=1, B=10 (Row 0)
        m1 = Marginal(attrs=('A', 'B'), values=(1, 10), target=0.9)
        self.marginals = MarginalSet([m1])

    def test_ilp_repair(self):
        try:
            import gurobipy as gp
        except ImportError:
            self.skipTest("Gurobipy not installed")
            
        repairer = ILPRepairer(alpha=0.5) # Use higher alpha to avoid trivial N=0 solution
        repaired_ds = repairer.repair(self.ds, self.marginals)

        
        # In the new formulation (dividing by N), keeping only Row 0 (matches marginal 100%)
        # might be better than keeping Row 0 and Row 2 (matches marginal 50%)
        # because alpha is low (0.1), favoring marginal matching.
        
        # Should have removed Row 1 (conflicting)
        has_row_1 = ((repaired_ds.data['A'] == 1) & (repaired_ds.data['B'] == 20)).any()
        self.assertFalse(has_row_1, "Row 1 (conflicting) should have been removed")
        self.assertEqual(len(repaired_ds.get_violations()), 0)
        
        has_row_0 = ((repaired_ds.data['A'] == 1) & (repaired_ds.data['B'] == 10)).any()
        self.assertTrue(has_row_0, "Row 0 (beneficial) should have been kept")


if __name__ == "__main__":
    unittest.main()
