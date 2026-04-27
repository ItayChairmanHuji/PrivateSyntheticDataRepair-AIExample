import sys
import os
import pandas as pd
import numpy as np
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.repairing.vanilla_vc_repairer import VanillaVCRepairer
from src.repairing.weighted_vc_repairer import WeightedVCRepairer
from src.entities.dataset import DatasetWithViolations
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side
from src.entities.marginal import Marginal, MarginalSet

class TestVCRepairers(unittest.TestCase):

    def setUp(self):
        # A small dataset where Row 0 and Row 1 violate t1.A=t2.A & t1.B!=t2.B
        self.data = pd.DataFrame({
            'A': [1, 1, 2],
            'B': [10, 20, 10]
        })
        # DC: not(t1.A=t2.A & t1.B!=t2.B)
        p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
        p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
        self.dcs = DenialConstraints([DenialConstraint([p1, p2])])
        
        self.ds = DatasetWithViolations("dummy", self.data, self.dcs, "")
        
        # Marginals: say we want more of A=1, B=10 (Row 0)
        m1 = Marginal('A', 'B', 1, 10, 0.9) 
        self.marginals = MarginalSet([m1])

    def test_weighted_vc_deep_logic(self):
        # Data: Row 0 matches m1, Row 1 doesn't, Row 2 doesn't.
        # m1: (1, 10), target 0.9.
        # Current counts: C1 = 1. N = 3.
        # alpha = 0.5.
        
        repairer = WeightedVCRepairer(alpha=0.5)
        repairer._precompute_initial_state(self.ds, self.marginals)
        
        # 1. Verify Weight calculation
        # N' = 2. 
        # For Row 0 (matches m1): C1' = 0. w = 0.5 * |0/2 - 0.9| = 0.45
        # For Row 1 (no match): C1' = 1. w = 0.5 * |1/2 - 0.9| = 0.20
        active_indices = [0, 1]
        weights = repairer._calculate_weights(active_indices, len(self.marginals))
        
        self.assertAlmostEqual(weights[0], 0.45)
        self.assertAlmostEqual(weights[1], 0.20)
        
        # 2. Verify selection ratio
        # Degree(0) = 1, Degree(1) = 1.
        # argmin pick Row 1 to remove because 0.20 < 0.45.
        graph = repairer._build_conflict_graph(self.ds)
        best_v = repairer._pick_best_vertex(active_indices, weights, graph)
        self.assertEqual(best_v, 1)


    def test_vanilla_vc_repair(self):
        repairer = VanillaVCRepairer()
        repaired_ds = repairer.repair(self.ds, self.marginals)
        
        # Conflicts: (0, 1). Vanilla VC selects max degree. Both 0 and 1 have degree 1.
        # It should remove one of them.
        self.assertEqual(len(repaired_ds.data), 2)
        # Remaining data should have 0 violations
        self.assertEqual(len(repaired_ds.violations), 0)

    def test_weighted_vc_repair(self):
        # alpha=0.5. 
        # Conflict: Row 0 (A=1, B=10) vs Row 1 (A=1, B=20)
        # Marginal: A=1, B=10, target=0.9
        
        # Row 0 matches marginal, current freq 1/3. Surplus = 1/3 - 0.9 = -0.56 (under-represented)
        # Row 1 does not match marginal. Surplus = 0.
        
        # Weighted VC selects vertex to REMOVE.
        # Removal should favor keeping Row 0 because it helps satisfy the marginal.
        
        repairer = WeightedVCRepairer(alpha=0.5)
        repaired_ds = repairer.repair(self.ds, self.marginals)
        
        # It should remove Row 1 and keep Row 0.
        self.assertEqual(len(repaired_ds.data), 2)
        
        # Verify that (1, 10) was KEPT and (1, 20) was REMOVED
        # data.iloc[keep_indices]
        # Row 2 (2, 10) should also be kept as it has no conflicts.
        
        has_row_0 = ((repaired_ds.data['A'] == 1) & (repaired_ds.data['B'] == 10)).any()
        has_row_1 = ((repaired_ds.data['A'] == 1) & (repaired_ds.data['B'] == 20)).any()
        
        self.assertTrue(has_row_0, "Row 0 (beneficial) should have been kept")
        self.assertFalse(has_row_1, "Row 1 (conflicting and not beneficial) should have been removed")
        self.assertEqual(len(repaired_ds.violations), 0)

if __name__ == "__main__":
    unittest.main()
