import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from u_utilities.u_io import ResourceManager, PathResolver
from u_utilities.u_shared import Dataset
from u_utilities.u_shared.marginal import MarginalSet
from p_processes.p04_repairing.src.workers.repairing_worker import RepairingWorker
from p_processes.p04_repairing.src.engine.repairing_engine import RepairingEngine
from p_processes.p04_repairing.src.orchestration.repairing_orchestrator import RepairingOrchestrator

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
    synth_dir = resolver.get_synthetic_data_path("test_ds", "dummy_synth", 1.0, 42, 10).parent
    synth_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"A": [1, 2]}).to_csv(synth_dir / "data.csv", index=False)
    
    marg_dir = resolver.get_marginal_path("test_ds", 0.1).parent
    marg_dir.mkdir(parents=True, exist_ok=True)
    with open(marg_dir / "marginals.json", "w") as f:
        json.dump({"marginals": []}, f)
        
    return rpm_root, manager

@patch('pandas.read_csv')
def test_repairing_orchestrator(mock_read_csv, mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    mock_read_csv.return_value = pd.DataFrame({"A": [1, 2]})
    
    engine = RepairingEngine(manager=manager)
    worker = RepairingWorker(repairer=DummyRepairer())
    
    orchestrator = RepairingOrchestrator(
        engine=engine,
        worker=worker,
        dataset_name="test_ds",
        synthesizer_name="dummy_synth",
        repairer_name="dummy_repairer",
        epsilon=1.0,
        seed=42,
        size=10,
        noise_level=0.1,
        alpha=0.5
    )
    
    orchestrator.run()
    
    output_path = engine.resolve_repaired_data_path("test_ds", "dummy_repairer", "dummy_synth", 1.0, 42, 10, 0.5)
    assert output_path.exists()
    
    df = pd.read_csv(output_path)
    assert len(df) == 1
