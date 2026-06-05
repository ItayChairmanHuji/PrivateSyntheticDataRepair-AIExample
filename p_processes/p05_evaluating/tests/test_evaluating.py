import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from u_utilities.u_io import ResourceManager, PathResolver
from u_utilities.u_shared import Dataset
from p_processes.p05_evaluating.src.workers.evaluating_worker import EvaluatingWorker
from p_processes.p05_evaluating.src.engine.evaluating_engine import EvaluatingEngine
from p_processes.p05_evaluating.src.orchestration.evaluating_orchestrator import EvaluatingOrchestrator

class DummyEvaluator:
    def evaluate(self, result):
        return {"dummy": "metric"}

@pytest.fixture
def mock_rpm_env(tmp_path):
    rpm_root = tmp_path / "rpm"
    rpm_root.mkdir()
    
    resolver = PathResolver(root_dir=str(rpm_root))
    manager = ResourceManager(resolver=resolver)
    
    manager.load_dataset = MagicMock(return_value=Dataset(name="test_ds", data=pd.DataFrame({"A": [1, 2]}), target="A", dcs=None))
    
    # Create mock synthetic and repaired data
    synth_dir = resolver.get_synthetic_data_path("test_ds", "dummy_synth", 1.0, 42, 10).parent
    synth_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"A": [1, 2]}).to_csv(synth_dir / "data.csv", index=False)
    
    rep_dir = resolver.get_repaired_data_path("test_ds", "dummy_repairer", "dummy_synth", 1.0, 42, 10, 0.5).parent
    rep_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"A": [1]}).to_csv(rep_dir / "data.csv", index=False)
    
    return rpm_root, manager

@patch('pandas.read_csv')
def test_evaluating_orchestrator(mock_read_csv, mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    mock_read_csv.return_value = pd.DataFrame({"A": [1, 2]})
    
    engine = EvaluatingEngine(manager=manager)
    worker = EvaluatingWorker(evaluator=DummyEvaluator())
    
    orchestrator = EvaluatingOrchestrator(
        engine=engine,
        worker=worker,
        dataset_name="test_ds",
        synthesizer_name="dummy_synth",
        repairer_name="dummy_repairer",
        epsilon=1.0,
        seed=42,
        size=10,
        alpha=0.5,
        experiment_id="E001"
    )
    
    orchestrator.run()
    
    output_dir = engine.resolve_result_dir("E001", "latest")
    assert output_dir.exists()
    
    output_file = output_dir / "result_test_ds.json"
    assert output_file.exists()
    
    with open(output_file, "r") as f:
        data = json.load(f)
        assert data == {"dummy": "metric"}
