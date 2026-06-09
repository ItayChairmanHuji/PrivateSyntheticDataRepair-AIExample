import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from u_utilities.u_io import ResourceManager, PathResolver, DataMode
from u_utilities.u_shared import Dataset, Marginal, MarginalSet
from p_processes.p05_evaluating.src.core.evaluating_core import EvaluatingCore
from p_processes.p05_evaluating.src.core.evaluators.loss_function_evaluator import LossFunctionEvaluator
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
        epsilon=1.0, seed=42, size=10, noise_level="test_noise", alpha=0.5
    )
    rep_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"A": [1]}).to_csv(rep_path, index=False)

    manager.load_marginals = MagicMock(return_value=MarginalSet(marginals=[
        Marginal(attrs=("A",), values=(2,), target=0.5)
    ]))
    
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
        noise_level="test_noise",
        experiment_id="E001"
    )
    
    worker.run()
    
    output_dir = engine.resolve_result_dir("E001", "latest")
    assert output_dir.exists()
    
    output_file = output_dir / "result_test_ds_dummy_synth_dummy_repairer_1.0_42_10_test_noise_0.5.json"
    assert output_file.exists()
    
    with open(output_file, "r") as f:
        data = json.load(f)
        assert data == {"dummy": "metric"}

    manager.load_marginals.assert_called_once_with(dataset_name="test_ds", noise_level="test_noise")


def test_loss_function_uses_synthetic_size_and_marginals():
    private = Dataset(name="private", data=pd.DataFrame({"A": [1, 2]}), target="A", dcs=None)
    synthetic = Dataset(name="synthetic", data=pd.DataFrame({"A": [1, 1, 2, 2]}), target="A", dcs=None)
    repaired = Dataset(name="repaired", data=pd.DataFrame({"A": [1, 1]}), target="A", dcs=None)
    marginals = MarginalSet(marginals=[Marginal(attrs=("A",), values=(2,), target=0.5)])
    result = type("Result", (), {
        "private_dataset": private,
        "synthetic_dataset": synthetic,
        "repaired_dataset": repaired,
        "obtained_marginals": marginals,
        "metadata": {"repairer_params": {"alpha": 0.5}},
    })()

    metrics = LossFunctionEvaluator().evaluate(result)["loss_function"]

    assert metrics["synthetic"]["size_component"] == 0.0
    assert metrics["synthetic"]["marginal_component"] == 0.0
    assert metrics["repaired"]["size_component"] == 0.5
    assert metrics["repaired"]["marginal_component"] == 0.5
    assert metrics["repaired"]["total"] == 0.5
