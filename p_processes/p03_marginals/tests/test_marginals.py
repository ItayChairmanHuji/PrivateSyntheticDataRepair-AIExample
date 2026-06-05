import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import MagicMock
from u_utilities.u_io import ResourceManager, PathResolver
from u_utilities.u_shared import Dataset
from p_processes.p03_marginals.src.core.marginals_core import MarginalsCore
from p_processes.p03_marginals.src.engine import MarginalsEngine
from p_processes.p03_marginals.src.worker import MarginalsWorker

@pytest.fixture
def mock_rpm_env(tmp_path):
    rpm_root = tmp_path / "rpm"
    rpm_root.mkdir()
    
    resolver = PathResolver(root_dir=str(rpm_root))
    manager = ResourceManager(resolver=resolver)
    
    manager.load_dataset = MagicMock(return_value=Dataset(name="test_ds", data=pd.DataFrame({"A": [1, 2]}), target="A", dcs=None))
    
    return rpm_root, manager

def test_marginals_orchestrator(mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    
    # Mock data with at least two columns for 2-way marginals
    data = pd.DataFrame({"A": [1, 0, 1], "target": [1, 0, 1]})
    manager.load_dataset.return_value = Dataset(name="test_ds", data=data, target="target", dcs=None)
    
    engine = MarginalsEngine(manager=manager)
    core = MarginalsCore()
    
    worker = MarginalsWorker(
        engine=engine,
        core=core,
        dataset_name="test_ds",
        noise_level=0.1
    )
    
    worker.run()
    
    # Verify via manager since engine uses it
    output_path = manager.resolver.resolve("marginal", dataset_name="test_ds", noise_level=0.1)
    assert output_path.exists()
    
    with open(output_path, "r") as f:
        data = json.load(f)
        assert "marginals" in data
        assert len(data["marginals"]) > 0
