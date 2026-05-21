import unittest
import pandas as pd
from s02_synthesizing.src.components.smart_noise import SmartNoiseSynthesizer
from shared.entities.dataset import Dataset
from shared.entities.denial_constraints import DenialConstraints

class TestSynthesizingComponents(unittest.TestCase):
    def setUp(self):
        # Create a dummy dataset with more unique values to satisfy MST's selection logic
        self.data = pd.DataFrame({
            "age": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
            "income": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
        })
        self.dataset = Dataset(
            name="dummy",
            data=self.data,
            dcs=DenialConstraints([]),
            target="income"
        )

    def test_smart_noise_synthesizer_basic(self):
        # Use MWEM as it doesn't rely on the broken private-pgm dependency in this environment
        synthesizer = SmartNoiseSynthesizer(engine="mwem", epsilon=10.0)
        synthetic_dataset = synthesizer.synthesize(self.dataset)
        
        self.assertEqual(len(synthetic_dataset.data), len(self.dataset.data))
        self.assertListEqual(list(synthetic_dataset.data.columns), list(self.dataset.data.columns))
        self.assertEqual(synthetic_dataset.name, "dummy_mwem")

if __name__ == "__main__":
    unittest.main()
