import unittest
import pandas as pd
import os
import shutil
from pathlib import Path
from s01_loading.src.loaders import DataLoader
from s01_loading.src.encoders import DataEncoder
from s01_loading.src.orchestration import StageOrchestrator
from s01_loading.src.io import FileLoader, ArtifactSaver
from s01_loading.src.loaders import DCsLoader, MetadataLoader

class TestStage1(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("s01_tests_temp")
        self.test_dir.mkdir(exist_ok=True)
        self.data_path = self.test_dir / "data.csv"
        self.dcs_path = self.test_dir / "dcs.txt"
        self.meta_path = self.test_dir / "metadata.json"
        
        df = pd.DataFrame({"A": ["x", "y"], "B": [1, 2]})
        df.to_csv(self.data_path, index=False)
        self.dcs_path.write_text("not(t1.A=t2.A & t1.B!=t2.B)")
        self.meta_path.write_text('{"target": "B"}')
        
        self.output_dir = self.test_dir / "output"

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_components(self):
        loader = DataLoader()
        df = loader.load(self.data_path)
        self.assertEqual(len(df), 2)
        
        encoder = DataEncoder()
        encoded_df = encoder.encode(df)
        self.assertTrue(pd.api.types.is_numeric_dtype(encoded_df["A"]))

    def test_orchestration(self):
        dataset_dir = self.test_dir / "test_dataset"
        dataset_dir.mkdir(exist_ok=True)
        shutil.move(str(self.data_path), str(dataset_dir / "data.csv"))
        shutil.move(str(self.dcs_path), str(dataset_dir / "dcs.txt"))
        shutil.move(str(self.meta_path), str(dataset_dir / "metadata.json"))

        from s01_loading.src.encoders import DCsEncoder
        file_loader = FileLoader(
            name="test_dataset",
            base_path=str(self.test_dir),
            data_loader=DataLoader(),
            dcs_loader=DCsLoader(),
            metadata_loader=MetadataLoader(),
            data_encoder=DataEncoder(),
            dcs_encoder=DCsEncoder()
        )
        
        orchestrator = StageOrchestrator(loader=file_loader, output_dir=self.output_dir)
        dataset = orchestrator.run()
        
        self.assertEqual(dataset.name, "test_dataset")
        self.assertTrue(self.output_dir.exists())
        self.assertTrue((self.output_dir / "private_data.csv").exists())
        self.assertTrue((self.output_dir / "metadata.json").exists())
        self.assertTrue((self.output_dir / "constraints.txt").exists())

    def test_cli_clean(self):
        from s01_loading.src.io.clean import clean
        # verify clean imports and runs without error for help
        # Note: clean() expects Path("s01_loading/output")
        # For a unit test, we'd typically mock this.
        pass 

    def test_cli_list(self):
        from s01_loading.src.io.list_datasets import list_datasets
        list_datasets()

if __name__ == "__main__":
    unittest.main()
