import pytest
import pandas as pd
from pathlib import Path
from u_utilities.u_io import PathResolver, ResourceManager, DataMode, DataLoader
from u_utilities.u_shared import Dataset, DenialConstraints

@pytest.fixture
def temp_rpm_root(tmp_path):
    """Creates a mock RPM directory structure."""
    r_data = tmp_path / "r_resources" / "r_data"
    adult_private = r_data / "adult" / "private"
    adult_private.mkdir(parents=True)
    
    # Create metadata and dcs
    (adult_private / "metadata.json").write_text('{"name": "adult", "target": "income"}')
    (adult_private / "dcs.txt").write_text("t1.age > t1.age")
    (adult_private / "data.csv").write_text("age,income\n30,high")
    
    # Create a synthetic folder
    synth_dir = r_data / "adult" / "synthetic" / "aim" / "1.0" / "42" / "1000"
    synth_dir.mkdir(parents=True)
    (synth_dir / "data.csv").write_text("age,income\n25,low")
    
    return tmp_path

def test_path_resolver(temp_rpm_root):
    resolver = PathResolver(root_dir=str(temp_rpm_root))
    
    # Test private path
    path = resolver.resolve("data", name="adult", mode=DataMode.PRIVATE)
    assert path == temp_rpm_root / "r_resources" / "r_data" / "adult" / "private"
    
    # Test synthetic path
    path = resolver.resolve("data", name="adult", mode=DataMode.SYNTHETIC, 
                            synth_name="aim", epsilon=1.0, seed=42, size=1000)
    assert "synthetic" in str(path)
    assert path.name == "data.csv"

def test_data_loader_discovery(temp_rpm_root):
    loader = DataLoader()
    synth_path = temp_rpm_root / "r_resources" / "r_data" / "adult" / "synthetic" / "aim" / "1.0" / "42" / "1000" / "data.csv"
    
    # This should trigger _discover_context
    dataset = loader.load(synth_path)
    
    assert dataset.name == "adult"
    assert dataset.target == "income"
    assert len(dataset.data) == 1
    assert "age" in dataset.data.columns

def test_resource_manager_di(temp_rpm_root):
    resolver = PathResolver(root_dir=str(temp_rpm_root))
    manager = ResourceManager(resolver=resolver)
    
    # Load private
    ds = manager.load_dataset("adult")
    assert ds.name == "adult"
    
    # Load synthetic
    ds_synth = manager.load_dataset("adult", mode=DataMode.SYNTHETIC,
                                   synth_name="aim", epsilon=1.0, seed=42, size=1000)
    assert ds_synth.name == "adult"
    assert ds_synth.data.iloc[0]["age"] == 25
