import unittest
import pandas as pd
import json
import shutil
import sys
import subprocess
from pathlib import Path
from shared.entities.marginal import Marginal, MarginalSet

class TestFileObtainer(unittest.TestCase):
    def setUp(self):
        self.test_dataset = "test_file_obtainer"
        self.input_dir = Path("s03_marginals/input") / self.test_dataset
        self.output_dir = Path("s03_marginals/output") / self.test_dataset
        self.temp_dir = Path("s03_temp_test")
        
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy inputs
        df = pd.DataFrame({"A": [0, 1], "B": [0, 1]})
        df.to_csv(self.input_dir / "private_data.csv", index=False)
        df.to_csv(self.input_dir / "synthetic_data.csv", index=False)
        with open(self.input_dir / "metadata.json", "w") as f:
            json.dump({"name": "test_file_obtainer", "target": "B"}, f)
        with open(self.input_dir / "constraints.txt", "w") as f:
            f.write("")
            
        # Create a pre-existing marginals file
        self.marginals_file = self.temp_dir / "pre_existing_marginals.json"
        marginals = MarginalSet([
            Marginal(attrs=("A",), values=(0,), target=0.5)
        ])
        with open(self.marginals_file, "w") as f:
            json.dump(marginals.to_dict(), f)

    def tearDown(self):
        if self.input_dir.exists():
            shutil.rmtree(self.input_dir)
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_file_obtainer_flow(self):
        """Verify that FileObtainer loads marginals from a file correctly."""
        cmd_main = [
            sys.executable, "s03_marginals/src/main.py", 
            "--config-name", "from_file",
            f"experiment_name={self.test_dataset}",
            f"path={self.marginals_file}"
        ]
        result = subprocess.run(cmd_main, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"main.py failed: {result.stderr}")
        self.assertIn("Success", result.stdout)

        # Verify output content
        output_file = self.output_dir / "marginals.json"
        self.assertTrue(output_file.exists())
        with open(output_file, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data["marginals"]), 1)
            self.assertEqual(data["marginals"][0]["target"], 0.5)

if __name__ == "__main__":
    unittest.main()
