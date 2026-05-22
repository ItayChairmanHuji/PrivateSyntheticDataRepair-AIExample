import unittest
import pandas as pd
import json
import shutil
import subprocess
import sys
from pathlib import Path

class TestStage3(unittest.TestCase):
    def setUp(self):
        self.test_dataset = "test_dummy"
        self.input_dir = Path("s03_marginals/input") / self.test_dataset
        self.output_dir = Path("s03_marginals/output") / self.test_dataset
        self.input_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy inputs
        df = pd.DataFrame({
            "A": [0, 1, 0, 1, 0, 1], 
            "B": [0, 0, 1, 1, 0, 0], 
            "C": [1, 0, 1, 0, 1, 0]
        })
        df.to_csv(self.input_dir / "private_data.csv", index=False)
        df.to_csv(self.input_dir / "synthetic_data.csv", index=False)
        with open(self.input_dir / "metadata.json", "w") as f:
            json.dump({"name": "test_dummy", "target": "B"}, f)
        with open(self.input_dir / "constraints.txt", "w") as f:
            f.write("")

    def tearDown(self):
        if self.input_dir.exists():
            shutil.rmtree(self.input_dir)
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)

    def test_full_api_flow(self):
        """Verify the full CLI flow as documented in CONTEXT.md."""
        # 1. Run main.py
        cmd_main = [
            sys.executable, "s03_marginals/src/main.py", 
            f"dataset_name={self.test_dataset}",
            "k=2"
        ]
        result = subprocess.run(cmd_main, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"main.py failed: {result.stderr}")
        self.assertIn("Success", result.stdout)

        # 2. Verify output content
        output_file = self.output_dir / "marginals.json"
        self.assertTrue(output_file.exists())
        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertIn("marginals", data)
            self.assertEqual(len(data["marginals"]), 2)
            # Check structure of a single marginal
            m = data["marginals"][0]
            self.assertIn("attrs", m)
            self.assertIn("values", m)
            self.assertIn("target", m)

        # 3. Run clean.py
        cmd_clean = [
            sys.executable, "s03_marginals/src/io/clean.py", 
            "--dataset", self.test_dataset
        ]
        result_clean = subprocess.run(cmd_clean, capture_output=True, text=True)
        self.assertEqual(result_clean.returncode, 0, f"clean.py failed: {result_clean.stderr}")
        self.assertFalse(self.output_dir.exists())

if __name__ == "__main__":
    unittest.main()
