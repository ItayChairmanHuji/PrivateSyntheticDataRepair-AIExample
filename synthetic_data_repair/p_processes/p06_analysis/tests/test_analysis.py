import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock
from u_utilities.u_io import ResourceManager, PathResolver
from p_processes.p06_analysis.src.workers.analysis_worker import AnalysisWorker
from p_processes.p06_analysis.src.engine.analysis_engine import AnalysisEngine
from p_processes.p06_analysis.src.orchestration.analysis_orchestrator import AnalysisOrchestrator

class DummyAnalyzer:
    def analyze(self, results, output_dir):
        with open(output_dir / "summary.json", "w") as f:
            json.dump({"count": len(results)}, f)

@pytest.fixture
def mock_rpm_env(tmp_path):
    rpm_root = tmp_path / "rpm"
    rpm_root.mkdir()
    
    resolver = PathResolver(root_dir=str(rpm_root))
    manager = ResourceManager(resolver=resolver)
    
    # Create mock result data
    result_dir = resolver.get_result_dir("E001", "latest")
    result_dir.mkdir(parents=True, exist_ok=True)
    with open(result_dir / "res1.json", "w") as f:
        json.dump({"val": 1}, f)
    with open(result_dir / "res2.json", "w") as f:
        json.dump({"val": 2}, f)
        
    return rpm_root, manager

def test_analysis_orchestrator(mock_rpm_env):
    rpm_root, manager = mock_rpm_env
    
    engine = AnalysisEngine(manager=manager)
    worker = AnalysisWorker(analyzer=DummyAnalyzer())
    
    orchestrator = AnalysisOrchestrator(
        engine=engine,
        worker=worker,
        experiment_id="E001"
    )
    
    orchestrator.run()
    
    output_dir = engine.resolve_analysis_dir("E001")
    assert output_dir.exists()
    
    output_file = output_dir / "summary.json"
    assert output_file.exists()
    
    with open(output_file, "r") as f:
        data = json.load(f)
        assert data["count"] == 2
