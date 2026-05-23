import unittest
import pandas as pd
import json
import shutil
from pathlib import Path
from s04_repairing.src.orchestration import StageOrchestrator
from s04_repairing.src.io import FileLoader, ArtifactSaver
from s04_repairing.src.repair import VanillaVCRepairer
from shared.entities.marginal import MarginalSet

class TestStage4(unittest.TestCase):
    def setUp(self):
        self.experiment_name = "test_dataset"
        self.base_dir = Path("s04_tests_temp")
        self.input_dir = self.base_dir / "input" / self.experiment_name
        self.output_dir = self.base_dir / "output" / self.experiment_name
        
        self.input_dir.mkdir(parents=True, exist_ok=True)
        
        # Create dummy artifacts
        df = pd.DataFrame({"A": [1, 1], "B": [10, 20]})
        df.to_csv(self.input_dir / "synthetic_data.csv", index=False)
        
        with open(self.input_dir / "metadata.json", "w") as f:
            json.dump({"name": "test", "target": "B"}, f)
            
        with open(self.input_dir / "constraints.txt", "w") as f:
            f.write("not(t1.A=t2.A & t1.B!=t2.B)")
            
        from shared.entities.marginal import Marginal, MarginalSet
        marginals = MarginalSet([
            Marginal(attrs=("A",), values=(1,), target=1.0)
        ])
        with open(self.input_dir / "marginals.json", "w") as f:
            json.dump(marginals.to_dict(), f)

    def tearDown(self):
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

    def test_orchestration(self):
        # 1. Instantiate components
        repairer = VanillaVCRepairer(alpha=0.5)
        loader = FileLoader(experiment_name=self.experiment_name, base_path=str(self.base_dir / "input"))
        saver = ArtifactSaver(experiment_name=self.experiment_name, base_path=str(self.base_dir / "output"))

        # 2. Orchestrate
        orchestrator = StageOrchestrator(
            experiment_name=self.experiment_name,
            repairer=repairer,
            loader=loader,
            saver=saver
        )
        orchestrator.run()
        
        # 3. Verify
        repaired_path = self.output_dir / "repaired_data.csv"
        self.assertTrue(repaired_path.exists())
        
        repaired_df = pd.read_csv(repaired_path)
        # In this dummy case, both tuples conflict, Max Degree (or any VC) should pick one to remove.
        self.assertEqual(len(repaired_df), 1)

    def test_cli_clean(self):
        from s04_repairing.src.io.clean import clean
        # Just verify it runs without crashing
        clean(self.experiment_name)

    def test_cli_list(self):
        from s04_repairing.src.io.list_repairers import list_repairers
        list_repairers()

if __name__ == "__main__":
    unittest.main()
