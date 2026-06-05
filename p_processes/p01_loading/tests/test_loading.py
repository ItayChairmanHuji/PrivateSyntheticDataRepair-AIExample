import pytest
import pandas as pd
import json
from pathlib import Path
from u_utilities.u_io import ResourceManager, PathResolver
from u_utilities.u_loading.src.loaders import DataLoader, DCsLoader, MetadataLoader
from u_utilities.u_loading.src.encoders import DataEncoder, DCsEncoder
from u_utilities.u_loading.src.loading_resolver import LoadingResolver
from p_processes.p01_loading.src.core.loading_core import LoadingCore
from p_processes.p01_loading.src.engine import LoadingEngine
from p_processes.p01_loading.src.worker import LoadingWorker

@pytest.fixture
def temp_loading_env(tmp_path):
    """Sets up a mock raw data directory and a mock RPM root."""
    # Setup raw data
    raw_dir = tmp_path / "data" / "test_ds" / "base"
    raw_dir.mkdir(parents=True)
    pd.DataFrame({"A": ["x", "y"], "B": [1, 2]}).to_csv(raw_dir / "original_data.csv", index=False)
    (raw_dir / "dcs.txt").write_text("not(t1.A=t2.A & t1.B!=t2.B)")
    (raw_dir / "metadata.json").write_text('{"target": "B"}')
    
    # Setup RPM root
    rpm_root = tmp_path / "rpm"
    rpm_root.mkdir()
    
    return raw_dir.parent, rpm_root

def test_loading_orchestrator(temp_loading_env):
    """Verifies the full Triad orchestration of the loading process."""
    raw_dir, rpm_root = temp_loading_env
    
    # 1. Initialize Engine
    manager = ResourceManager(resolver=PathResolver(root_dir=str(rpm_root)))
    engine = LoadingEngine(manager=manager)
    
    # 2. Initialize Logic
    resolver = LoadingResolver(base_path=str(raw_dir.parent), dataset_name="test_ds")
    core = LoadingCore(
        resolver=resolver,
        data_loader=DataLoader(),
        dcs_loader=DCsLoader(),
        metadata_loader=MetadataLoader(),
        data_encoder=DataEncoder(),
        dcs_encoder=DCsEncoder()
    )
    
    # 3. Initialize Orchestrator
    worker = LoadingWorker(engine=engine, core=core)
    
    # 4. Run the process
    worker.run()
    
    # 5. Verify physical side-effects
    expected_dir = rpm_root / "r_resources" / "r_data" / "test_ds" / "private"
    assert expected_dir.exists()
    assert (expected_dir / "data.csv").exists()
    assert (expected_dir / "metadata.json").exists()
    assert (expected_dir / "dcs.txt").exists()
    
    # 6. Verify data integrity and serialization
    with open(expected_dir / "metadata.json", "r") as f:
        meta = json.load(f)
        assert meta["name"] == "test_ds"
        assert "mappings" in meta
        assert "A" in meta["mappings"]
        # LabelEncoder mappings should be serialized as dicts
        assert isinstance(meta["mappings"]["A"], dict)
