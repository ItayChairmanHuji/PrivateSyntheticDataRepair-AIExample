import unittest
import pandas as pd
import os
from s01_loading.src.components.data_loader import DataLoader
from s01_loading.src.components.data_encoder import DataEncoder

class TestLoadingComponents(unittest.TestCase):
    def setUp(self):
        self.loader = DataLoader()
        self.encoder = DataEncoder()
        self.test_csv = "test_data.csv"
        df = pd.DataFrame({
            "A": ["x", "y", "x"],
            "B": [1, 2, 1],
            "C": ["a", "b", "c"]
        })
        df.to_csv(self.test_csv, index=False)

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_data_loader(self):
        df = self.loader.load(self.test_csv)
        self.assertEqual(len(df), 3)
        self.assertListEqual(list(df.columns), ["A", "B", "C"])

    def test_data_encoder(self):
        df = self.loader.load(self.test_csv)
        encoded_df = self.encoder.encode(df)
        
        # Numeric column 'B' should remain unchanged or at least be numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(encoded_df["B"]))
        
        # Categorical columns 'A' and 'C' should now be numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(encoded_df["A"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(encoded_df["C"]))
        
        # Check mappings
        mappings = self.encoder.get_mappings()
        self.assertIn("A", mappings)
        self.assertIn("C", mappings)
        self.assertNotIn("B", mappings)
        
        # Check specific encoding for 'A' ('x' -> 0, 'y' -> 1 or vice versa)
        self.assertEqual(len(set(encoded_df["A"])), 2)

if __name__ == "__main__":
    unittest.main()
