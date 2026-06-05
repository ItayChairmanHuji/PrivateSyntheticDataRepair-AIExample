import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from u_utilities.u_io import ResourceManager, PathResolver, DataMode
from u_utilities.u_shared import Dataset, MarginalSet
from p_processes.p04_repairing.src.core.repairing_core import RepairingCore
from p_processes.p04_repairing.src.engine import RepairingEngine
from p_processes.p04_repairing.src.worker import RepairingWorker

class DummyRepairer:
    def repair(self, dataset, marginals):
        # Dummy repair just returns a smaller dataset
        return Dataset(name=dataset.name, data=pd.DataFrame({"A": [1]}), target=dataset.target, dcs=dataset.dcs)

@pytest.fixture
def mock_rpm_env(tmp_path):
    rpm_root = tmp_path / "rpm"
    rpm_root.mkdir()
    
    resolver = PathResolver(root_dir=str(rpm_root))
    manager = ResourceManager(resolver=resolver)
    
    manager.load_dataset = MagicMock(return_value=Dataset(name="test_ds", data=pd.DataFrame({"A": [1, 2]}), target="A", dcs=None))
    
    # Create mock synthetic data and marginals
    synth_path = manager.resolver.resolve(
        "data", name="test_ds", mode=DataMode.SYNTHETIC, 
        synth_name="dummy_synth", epsilon=1.0, seed=42, size=10
    )
    synth_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"A": [1, 2]}).to_csv(synth_path, index=False)
    
    marg_path = manager.resolver.resolve("marginal", dataset_name="test_ds", noise_level=0.1)
    marg_path.parent.mkdir(parents=True, exist_ok=True)
    with open(marg_path, "w") as f:
        json.dump({"marginals": []}, f)
        
    return rpm_root, manager

def test_repairing_orchestrator(mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    
    engine = RepairingEngine(manager=manager)
    core = RepairingCore(repairer=DummyRepairer())
    
    worker = RepairingWorker(
        engine=engine,
        core=core,
        dataset_name="test_ds",
        synthesizer_name="dummy_synth",
        repairer_name="dummy_repairer",
        epsilon=1.0,
        seed=42,
        size=10,
        noise_level=0.1,
        alpha=0.5
    )
    
    worker.run()
    
    output_path = engine.resolve_repaired_data_path("test_ds", "dummy_repairer", "dummy_synth", 1.0, 42, 10, 0.5)
    assert output_path.exists()
    
    # Check the repaired data
    df = pd.read_csv(output_path)
    assert len(df) == 1
    assert df.iloc[0]["A"] == 1
