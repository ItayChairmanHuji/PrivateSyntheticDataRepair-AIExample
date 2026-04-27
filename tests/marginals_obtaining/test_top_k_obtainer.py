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
from src.entities.denial_constraints import DenialConstraints

class TestTopKObtainer(unittest.TestCase):

    def setUp(self):
        self.p_data = pd.DataFrame({
            'A': [1, 1, 0, 0],
            'B': [1, 1, 1, 0]
        })
        self.s_data = pd.DataFrame({
            'A': [1, 0, 0, 0],
            'B': [0, 0, 1, 1]
        })
        
        self.p_ds = Dataset("private", self.p_data, DenialConstraints([]), "")
        self.s_ds = Dataset("synthetic", self.s_data, DenialConstraints([]), "")
        
        self.utility = DistanceUtility()
        self.obtainer = TopKObtainer(
            selection_budget=1.0,
            generation_budget=1.0,
            k=2,
            utility_function=self.utility
        )

    def test_compute_all_2way_marginals(self):
        # Only one pair (A, B)
        # Pairs: (1,1) -> 2/4 = 0.5, (0,1) -> 1/4 = 0.25, (0,0) -> 1/4 = 0.25
        freqs = self.obtainer._compute_all_2way_marginals(self.p_data)
        self.assertEqual(len(freqs), 3)
        self.assertEqual(freqs[('A', 'B', 1, 1)], 0.5)
        self.assertEqual(freqs[('A', 'B', 0, 1)], 0.25)
        self.assertEqual(freqs[('A', 'B', 0, 0)], 0.25)

    def test_obtain_k_limit(self):
        # Request k=2, should return at most 2
        marginal_set = self.obtainer.obtain(self.p_ds, self.s_ds)
        self.assertLessEqual(len(marginal_set), 2)
        
    def test_obtain_noisy_values(self):
        # Values should be roughly around the original but with noise
        marginal_set = self.obtainer.obtain(self.p_ds, self.s_ds)
        for m in marginal_set:
            self.assertTrue(0.0 <= m.target <= 1.0)
            self.assertIsInstance(m.target, float)

    def test_zero_budget_handling(self):
        # Even with low budget it should work (though very noisy)
        low_budget_obtainer = TopKObtainer(
            selection_budget=0.001,
            generation_budget=0.001,
            k=5,
            utility_function=self.utility
        )
        marginal_set = low_budget_obtainer.obtain(self.p_ds, self.s_ds)
        self.assertIsInstance(len(marginal_set), int)

if __name__ == "__main__":
    unittest.main()
