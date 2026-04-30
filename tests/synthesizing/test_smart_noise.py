import sys
import os
import pandas as pd
import unittest
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.synthesizing.smart_noise import SmartNoiseSynthesizer
from src.entities.dataset import Dataset
from src.entities.denial_constraints import DenialConstraints

class TestSmartNoiseSynthesizer(unittest.TestCase):
    """
    Consolidated test suite for SmartNoiseSynthesizer.
    Covers MST, AIM, and PATECTGAN algorithms.
    """

    def setUp(self):
        # Create a small mixed-type dataset for synthesis
        np.random.seed(42)
        self.data = pd.DataFrame({
            'Cat1': np.random.choice(['A', 'B', 'C'], 100),
            'Cat2': np.random.choice(['Low', 'High'], 100),
            'Num1': np.random.normal(50, 10, 100).astype(int)
        })
        self.dcs = DenialConstraints([])
        self.ds = Dataset("test_ds", self.data, self.dcs, "Cat1")

    def _verify_synthesis(self, result, engine_name):
        """Helper to verify the structure of synthetic output."""
        self.assertEqual(len(result.data), len(self.data), f"{engine_name} failed to produce correct row count")
        self.assertListEqual(list(result.data.columns), list(self.data.columns), f"{engine_name} altered columns")
        self.assertFalse(result.data.isnull().all().all(), f"{engine_name} produced all nulls")

    def test_mst_algorithm(self):
        """Verify MST algorithm integration."""
        synth = SmartNoiseSynthesizer(engine="mst", epsilon=1.0)
        result = synth.synthesize(self.ds)
        self._verify_synthesis(result, "MST")

    def test_aim_algorithm(self):
        """Verify AIM algorithm integration."""
        synth = SmartNoiseSynthesizer(engine="aim", epsilon=1.0)
        result = synth.synthesize(self.ds)
        self._verify_synthesis(result, "AIM")

    def test_patectgan_algorithm(self):
        """Verify PATECTGAN algorithm integration."""
        # PATECTGAN can be slow, using minimal epochs for test speed
        synth = SmartNoiseSynthesizer(engine="patectgan", epsilon=1.0, epochs=1)
        result = synth.synthesize(self.ds)
        self._verify_synthesis(result, "PATECTGAN")

    def test_kwargs_transparency(self):
        """Ensure kwargs are passed correctly to the underlying snsynth."""
        # Test the dictionary-style kwargs support
        synth = SmartNoiseSynthesizer(engine="patectgan", epsilon=1.0, kwargs={"epochs": 1})
        self.assertIn("epochs", synth.kwargs)
        self.assertEqual(synth.kwargs["epochs"], 1)
        
        result = synth.synthesize(self.ds)
        self._verify_synthesis(result, "PATECTGAN with nested kwargs")

    def test_column_consistency(self):
        """Ensure synthetic data has the same columns as original."""
        synth = SmartNoiseSynthesizer(engine="patectgan", epsilon=10.0, epochs=1)
        result = synth.synthesize(self.ds)
        self.assertEqual(set(result.data.columns), set(self.data.columns))

if __name__ == "__main__":
    unittest.main()
