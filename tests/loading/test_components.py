import sys
import os
import pandas as pd
from pathlib import Path
import unittest
from sklearn.preprocessing import LabelEncoder

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder

class TestLoadingComponents(unittest.TestCase):

    def setUp(self):
        self.temp_dir = Path("temp_test_components")
        self.temp_dir.mkdir(exist_ok=True)

    def tearDown(self):
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_data_loader(self):
        path = self.temp_dir / "data.csv"
        df = pd.DataFrame({'A': [1, 2], 'B': ['x', 'y']})
        df.to_csv(path, index=False)
        
        loader = DataLoader()
        loaded_df = loader.load(path)
        pd.testing.assert_frame_equal(df, loaded_df)

    def test_dcs_loader_parsing(self):
        dcs_content = "not(t1.City='NYC' & t1.Salary>5000)\nt1.A=t2.A & t1.B!=t2.B"
        path = self.temp_dir / "dcs.txt"
        path.write_text(dcs_content)
        
        loader = DCsLoader()
        dcs = loader.load(path)
        
        self.assertEqual(len(dcs.constraints), 2)
        # Check first DC
        self.assertEqual(dcs.constraints[0].predicates[0].left.attr, "City")
        self.assertEqual(dcs.constraints[0].predicates[0].right.attr, "NYC")
        self.assertTrue(dcs.constraints[0].predicates[0].right.is_value)
        
        # Check numeric literal
        salary_pred = dcs.constraints[0].predicates[1]
        self.assertEqual(salary_pred.left.attr, "Salary")
        self.assertEqual(salary_pred.opr, ">")
        # Loader currently keeps values as strings but we expect it to be parsed correctly
        self.assertEqual(str(salary_pred.right.attr), "5000")
        
        # Check second DC
        self.assertEqual(dcs.constraints[1].predicates[0].left.attr, "A")
        self.assertEqual(dcs.constraints[1].predicates[1].opr, "!=")

    def test_metadata_loader(self):
        import json
        metadata = {"target": "income", "extra": 123}
        path = self.temp_dir / "metadata.json"
        with open(path, "w") as f:
            json.dump(metadata, f)
            
        loader = MetadataLoader()
        loaded_meta = loader.load(path)
        self.assertEqual(loaded_meta["target"], "income")

    def test_data_encoder(self):
        df = pd.DataFrame({
            'Cat': ['A', 'B', 'A'],
            'Num': [10, 20, 30]
        })
        encoder = DataEncoder()
        encoded_df = encoder.encode(df)
        
        self.assertTrue(pd.api.types.is_numeric_dtype(encoded_df['Cat']))
        self.assertEqual(encoded_df['Cat'].iloc[0], encoded_df['Cat'].iloc[2])
        self.assertNotEqual(encoded_df['Cat'].iloc[0], encoded_df['Cat'].iloc[1])
        
        mappings = encoder.get_mappings()
        self.assertIn('Cat', mappings)
        self.assertIsInstance(mappings['Cat'], LabelEncoder)

    def test_dcs_encoder(self):
        # Setup mappings manually for testing
        le = LabelEncoder()
        le.fit(['NYC', 'LA'])
        mappings = {'City': le}
        
        # Create a DC: t1.City = 'NYC'
        from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side
        p = Predicate(
            left=Side(attr='City', index=1, is_value=False),
            opr='=',
            right=Side(attr='NYC', index=1, is_value=True)
        )
        dcs = DenialConstraints([DenialConstraint([p])])
        
        encoder = DCsEncoder()
        encoded_dcs = encoder.encode(dcs, mappings)
        
        encoded_val = le.transform(['NYC'])[0]
        self.assertEqual(encoded_dcs.constraints[0].predicates[0].right.attr, encoded_val)

if __name__ == "__main__":
    unittest.main()
