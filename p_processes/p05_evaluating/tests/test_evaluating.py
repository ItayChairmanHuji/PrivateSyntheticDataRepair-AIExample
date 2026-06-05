import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from u_utilities.u_io import ResourceManager, PathResolver, DataMode
from u_utilities.u_shared import Dataset
from p_processes.p05_evaluating.src.core.evaluating_core import EvaluatingCore
from p_processes.p05_evaluating.src.engine import EvaluatingEngine
from p_processes.p05_evaluating.src.worker import EvaluatingWorker

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
    synth_path = manager.resolver.resolve(
        "data", name="test_ds", mode=DataMode.SYNTHETIC, 
        synth_name="dummy_synth", epsilon=1.0, seed=42, size=10
    )
    synth_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"A": [1, 2]}).to_csv(synth_path, index=False)
    
    rep_path = manager.resolver.resolve(
        "data", name="test_ds", mode=DataMode.REPAIRED,
        repairer_name="dummy_repairer", synth_name="dummy_synth",
        epsilon=1.0, seed=42, size=10, alpha=0.5
    )
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"A": [1]}).to_csv(rep_path, index=False)
    
    return rpm_root, manager

def test_evaluating_orchestrator(mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    
    engine = EvaluatingEngine(manager=manager)
    core = EvaluatingCore(evaluator=DummyEvaluator())
    
    worker = EvaluatingWorker(
        engine=engine,
        core=core,
        dataset_name="test_ds",
        synthesizer_name="dummy_synth",
        repairer_name="dummy_repairer",
        epsilon=1.0,
        seed=42,
        size=10,
        alpha=0.5,
        experiment_id="E001"
    )
    
    worker.run()
    
    output_dir = engine.resolve_result_dir("E001", "latest")
    assert output_dir.exists()
    
    output_file = output_dir / "result_test_ds.json"
    assert output_file.exists()
    
    with open(output_file, "r") as f:
        data = json.load(f)
        assert data == {"dummy": "metric"}
