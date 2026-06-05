import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import MagicMock
from u_utilities.u_io import ResourceManager, PathResolver
from u_utilities.u_shared import Dataset
from p_processes.p03_marginals.src.workers.marginals_worker import MarginalsWorker
from p_processes.p03_marginals.src.engine.marginals_engine import MarginalsEngine
from p_processes.p03_marginals.src.orchestration.marginals_orchestrator import MarginalsOrchestrator

class DummyCalculator:
    def calculate(self, dataset):
        return {"dummy": "marginal"}

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
    
    engine = MarginalsEngine(manager=manager)
    worker = MarginalsWorker(calculator=DummyCalculator())
    
    orchestrator = MarginalsOrchestrator(
        engine=engine,
        worker=worker,
        dataset_name="test_ds",
        noise_level=0.1
    )
    
    orchestrator.run()
    
    output_path = engine.resolve_marginal_path("test_ds", 0.1)
    assert output_path.exists()
    
    with open(output_path, "r") as f:
        data = json.load(f)
        assert data == {"dummy": "marginal"}
