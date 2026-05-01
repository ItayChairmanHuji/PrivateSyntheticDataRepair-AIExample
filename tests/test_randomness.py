import unittest
import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.synthesizing.co_noise import CoNoise
from src.marginals_obtaining.top_k_obtainer import TopKObtainer
from src.marginals_obtaining.utility_functions.distance_utility import DistanceUtility
from src.entities.dataset import Dataset
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

class TestRandomness(unittest.TestCase):

    def setUp(self):
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50]
        })
        p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
        p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
        self.dcs = DenialConstraints([DenialConstraint([p1, p2])])
        self.ds = Dataset("test", self.data, self.dcs, "")

    def test_co_noise_deterministic_change(self):
        # With seed 42, num_iterations=1, let's see exactly what happens
        cn = CoNoise(num_of_iterations=1, seed=42)
        res = cn.synthesize(self.ds)
        
        # We expect exactly one pair of tuples to be modified to violate the FD.
        # Since the original data has all unique A values, any violation requires making A equal and B different.
        
        # Let's find the violations in the result
        from src.loading.violation_finder import ViolationFinder
        v = ViolationFinder().find_violations(res.data, self.dcs)
        
        self.assertEqual(len(v), 1, "Should have introduced exactly one violating pair")
        idx1, idx2 = v.iloc[0]['idx1'], v.iloc[0]['idx2']
        
        # Assert that with seed 42, it picked these specific rows (Stable across environments due to random.seed)
        # On my local run with seed 42, it picked (0, 2).
        self.assertEqual((idx1, idx2), (0, 2))

    def test_top_k_deterministic_selection(self):
        # Pool of 2 potential marginals. 
        # m1 has huge distance (utility), m2 has small distance.
        # With seed 42 and k=1, m1 should ALWAYS be selected.
        
        p_ds = Dataset("p", pd.DataFrame({'A':[1,1,1,1], 'B':[1,1,1,1], 'C':[1,1,1,1]}), DenialConstraints([]), "") 
        s_ds = Dataset("s", pd.DataFrame({'A':[0,0,0,0], 'B':[0,0,0,0], 'C':[1,1,1,0]}), DenialConstraints([]), "") 
        
        utility = DistanceUtility()
        # Use a reasonable budget (100.0)
        obtainer = TopKObtainer(selection_budget=100.0, generation_budget=100.0, k=1, utility_function=utility)
        
        np.random.seed(42)
        m_set = obtainer.obtain(p_ds, s_ds)
        
        self.assertEqual(len(m_set), 1)
        selected = m_set.marginals[0]
        # (A,B,1,1) utility is 1.0. (A,C,1,1) utility is 0.25. (B,C,1,1) utility is 0.25.
        self.assertEqual(selected.attrs[0], 'A')
        self.assertEqual(selected.attrs[1], 'B')
        self.assertEqual(selected.values[0], 1)
        self.assertEqual(selected.values[1], 1)

if __name__ == "__main__":
    unittest.main()
