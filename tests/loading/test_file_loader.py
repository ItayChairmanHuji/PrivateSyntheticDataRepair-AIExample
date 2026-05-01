import sys
import os
import pandas as pd
import unittest
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.loading.file_loader import FileLoader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder

class TestFileLoaderIntegration(unittest.TestCase):

    def test_dummy_dataset_load(self):
        # Locate the data directory relative to this script
        # tests/loading/test_file_loader.py -> ../../data
        base_path = Path(__file__).parent.parent.parent / "data"
        
        if not (base_path / "dummy").exists():
            self.skipTest("Dummy dataset not found in data/dummy")

        loader = FileLoader(
            name="dummy",
            base_path=str(base_path),
            data_loader=DataLoader(),
            dcs_loader=DCsLoader(),
            metadata_loader=MetadataLoader(),
            data_encoder=DataEncoder(),
            dcs_encoder=DCsEncoder()
        )
        
        dataset = loader.load()
        
        # Basic validation
        self.assertEqual(dataset.name, "dummy")
        self.assertIsInstance(dataset.data, pd.DataFrame)
        self.assertFalse(dataset.data.empty)
        
        # Check that data is encoded
        for col in dataset.data.columns:
            self.assertTrue(pd.api.types.is_numeric_dtype(dataset.data[col]), f"Column {col} is not numeric")
            
        # Check violations
        violations = dataset.get_violations()
        self.assertIsInstance(violations, pd.DataFrame)
        self.assertGreater(len(violations), 0, "Expected violations in dummy dataset")
        self.assertIn('idx1', violations.columns)
        self.assertIn('idx2', violations.columns)

if __name__ == "__main__":
    unittest.main()
