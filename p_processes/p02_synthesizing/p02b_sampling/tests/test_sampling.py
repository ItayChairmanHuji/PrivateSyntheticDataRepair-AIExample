import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock
from u_utilities.u_io import ResourceManager, PathResolver
from u_utilities.u_shared import Dataset
from p_processes.p02_synthesizing.p02b_sampling.src.core.sampling_core import SamplingCore
from p_processes.p02_synthesizing.p02b_sampling.src.engine import SamplingEngine
from p_processes.p02_synthesizing.p02b_sampling.src.worker import SamplingWorker

class DummySampler:
    def sample(self, model, dataset, size):
        return Dataset(name=dataset.name, data=pd.DataFrame({"A": [1]*size}), target=dataset.target, dcs=dataset.dcs)

@pytest.fixture
def mock_rpm_env(tmp_path):
    rpm_root = tmp_path / "rpm"
    rpm_root.mkdir()
    
    resolver = PathResolver(root_dir=str(rpm_root))
    manager = ResourceManager(resolver=resolver)
    
    # Mock dcs
    mock_dcs = MagicMock()
    mock_dcs.to_string.return_value = "dummy_dcs"
    
    # Mock manager behavior since we just want to test orchestration and paths
    manager.load_dataset = MagicMock(return_value=Dataset(name="test_ds", data=pd.DataFrame({"A": [1, 2]}), target="A", dcs=mock_dcs))
    manager.load_model = MagicMock(return_value="dummy_model")
    
    return rpm_root, manager

def test_sampling_orchestrator(mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    
    engine = SamplingEngine(manager=manager)
    core = SamplingCore(sampler=DummySampler())
    
    worker = SamplingWorker(
        engine=engine,
        core=core,
        dataset_name="test_ds",
        engine_name="dummy_engine",
        epsilon=1.0,
        seed=42,
        size=10
    )
    
    worker.run()
    
    # Verify synthetic data path creation
    output_path = engine.resolve_synthetic_data_path("test_ds", "dummy_engine", 1.0, 42, 10)
    assert output_path.exists()
    
    # Verify output data
    df = pd.read_csv(output_path)
    assert len(df) == 10
    assert list(df.columns) == ["A"]
