import sys
import os
import pandas as pd
import numpy as np
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.marginals_obtaining.top_k_obtainer import TopKObtainer
from src.marginals_obtaining.utility_functions.distance_utility import DistanceUtility
from src.entities.dataset import Dataset
from src.entities.denial_constraints import Side, Predicate, DenialConstraint, DenialConstraints

class TestDCFiltering(unittest.TestCase):

    def setUp(self):
        # 3 columns: A, B, C
        self.p_data = pd.DataFrame({
            'A': [1, 1, 0, 0],
            'B': [1, 1, 1, 0],
            'C': [0, 1, 0, 1]
        })
        self.s_data = pd.DataFrame({
            'A': [0, 0, 0, 0],
            'B': [0, 0, 0, 0],
            'C': [0, 0, 0, 0]
        })
        
        # DC on 'A'
        side_a = Side(attr='A', index=1, is_value=False)
        pred = Predicate(left=side_a, opr='==', right=side_a)
        dc = DenialConstraint(predicates=[pred])
        self.dcs = DenialConstraints(constraints=[dc])
        
        self.p_ds = Dataset("private", self.p_data, self.dcs, "")
        self.s_ds = Dataset("synthetic", self.s_data, DenialConstraints([]), "")
        
        self.utility = DistanceUtility()
        self.obtainer = TopKObtainer(
            selection_budget=1.0,
            generation_budget=1.0,
            k=10, # Request many to see what we get
            utility_function=self.utility
        )

    def test_obtain_filters_dc_attrs(self):
        # Should NOT return any marginals containing 'A'
        marginal_set = self.obtainer.obtain(self.p_ds, self.s_ds)
        
        for m in marginal_set:
            self.assertNotIn('A', m.attrs, f"Marginal {m} contains filtered attribute 'A'")
            # Since A is filtered, only (B, C) pair should remain
            self.assertIn('B', m.attrs)
            self.assertIn('C', m.attrs)

    def test_obtain_all_filtered(self):
        # DC on all attributes
        side_a = Side(attr='A', index=1, is_value=False)
        side_b = Side(attr='B', index=1, is_value=False)
        side_c = Side(attr='C', index=1, is_value=False)
        dcs = DenialConstraints(constraints=[
            DenialConstraint([Predicate(side_a, '==', side_a)]),
            DenialConstraint([Predicate(side_b, '==', side_b)]),
            DenialConstraint([Predicate(side_c, '==', side_c)])
        ])
        p_ds = Dataset("private", self.p_data, dcs, "")
        
        marginal_set = self.obtainer.obtain(p_ds, self.s_ds)
        self.assertEqual(len(marginal_set), 0, "Should return no marginals when all attributes are in DCs")

if __name__ == "__main__":
    unittest.main()
