import pytest
import pandas as pd
from unittest.mock import MagicMock
from u_utilities.u_io import ResourceManager, PathResolver
from u_utilities.u_shared import Dataset
from p_processes.p02_synthesizing.p02a_training.src.engine import TrainingEngine
from p_processes.p02_synthesizing.p02a_training.src.core.training_core import TrainingCore
from p_processes.p02_synthesizing.p02a_training.src.worker import TrainingWorker

@pytest.fixture
def mock_rpm_env(tmp_path):
    rpm_root = tmp_path / "rpm"
    rpm_root.mkdir()
    
    resolver = PathResolver(root_dir=str(rpm_root))
    manager = ResourceManager(resolver=resolver)
    
    # Mock manager behavior
    manager.load_dataset = MagicMock(return_value=Dataset(name="test_ds", data=pd.DataFrame({"A": [1, 2]}), target="A", dcs=None))
    manager.save_model = MagicMock()
    
    return rpm_root, manager

def test_training_orchestrator(mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    
    engine = TrainingEngine(manager=manager)
    core = TrainingCore()
    
    # Mock trainer
    mock_trainer = MagicMock()
    mock_trainer.train.return_value = "trained_model_object"
    
    worker = TrainingWorker(engine=engine, core=core)
    
    cfg = MagicMock()
    cfg.dataset_name = "test_ds"
    cfg.engine = "mst"
    cfg.epsilon = 1.0
    cfg.seed = 42
    
    model_path = worker.run(cfg, mock_trainer)
    
    # Verify manager calls
    from unittest.mock import ANY
    manager.load_dataset.assert_called_with("test_ds", mode=ANY)
    mock_trainer.train.assert_called()
    manager.save_model.assert_called()
    
    # Verify return value is a Path
    from pathlib import Path
    assert isinstance(model_path, Path)
    assert "test_ds" in str(model_path)
    assert "mst" in str(model_path)
