import sys
import os
import pandas as pd
import numpy as np
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.synthesizing.co_noise import CoNoise
from src.entities.dataset import Dataset
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

class TestCoNoise(unittest.TestCase):

    def setUp(self):
        # A clean dataset: 10 rows with A and B
        # Let's ensure it has NO violations for not(t1.A=t2.A & t1.B!=t2.B)
        self.data = pd.DataFrame({
            'A': list(range(10)), # All A are different, so no violations of FD A->B
            'B': [100] * 10
        })
        # DC: not(t1.A=t2.A & t1.B!=t2.B)
        p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
        p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
        self.dcs = DenialConstraints([DenialConstraint([p1, p2])])
        
        self.ds = Dataset("private", self.data, self.dcs, "")

    def test_co_noise_introduces_violations(self):
        # Initial violations should be 0
        ds_with_v = Dataset(self.ds.name, self.ds.data, self.ds.dcs, self.ds.target)
        self.assertEqual(len(ds_with_v.get_violations()), 0)
        
        # Run Co-Noise
        synthesizer = CoNoise(num_of_iterations=5, seed=42)
        synthetic_ds = synthesizer.synthesize(self.ds)
        
        # Since we ran 5 iterations, we expect some modifications that lead to violations
        # In each iteration it picks 2 tuples and FORCES them to violate a DC.
        # So we should have at least 1 violation if iterations > 0 and DC exists.
        self.assertGreater(len(synthetic_ds.get_violations()), 0)
        
        # Ensure data shape is preserved
        self.assertEqual(synthetic_ds.data.shape, self.data.shape)

    def test_co_noise_reproducibility(self):
        synthesizer1 = CoNoise(num_of_iterations=2, seed=123)
        synthesizer2 = CoNoise(num_of_iterations=2, seed=123)
        
        res1 = synthesizer1.synthesize(self.ds)
        res2 = synthesizer2.synthesize(self.ds)
        
        pd.testing.assert_frame_equal(res1.data, res2.data)

    def test_co_noise_no_dcs(self):
        empty_dcs = DenialConstraints([])
        ds_no_dcs = Dataset("private", self.data, empty_dcs, "")
        
        synthesizer = CoNoise(num_of_iterations=5)
        res = synthesizer.synthesize(ds_no_dcs)
        
        # No DCs, so data should remain unchanged
        pd.testing.assert_frame_equal(res.data, self.data)

if __name__ == "__main__":
    unittest.main()
