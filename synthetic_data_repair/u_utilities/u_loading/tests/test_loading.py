import pytest
import pandas as pd
from pathlib import Path
from u_utilities.u_loading import ResourceLoader, LoadingResolver
from u_utilities.u_loading.src.loaders import DataLoader, DCsLoader, MetadataLoader
from u_utilities.u_loading.src.encoders import DataEncoder, DCsEncoder

@pytest.fixture
def mock_dataset_dir(tmp_path):
    dataset_dir = tmp_path / "adult"
    dataset_dir.mkdir()
    
    # Create data.csv
    df = pd.DataFrame({
        "age": [25, 30],
        "workclass": ["Private", "Public"]
    })
    df.to_csv(dataset_dir / "data.csv", index=False)
    
    # Create dcs.txt
    dcs_content = "not(t1.workclass='Private' & t1.age>20)"
    (dataset_dir / "dcs.txt").write_text(dcs_content)
    
    # Create metadata.json
    (dataset_dir / "metadata.json").write_text('{"target": "income"}')
    
    return tmp_path

def test_resource_loader_full_flow(mock_dataset_dir):
    resolver = LoadingResolver(base_path=str(mock_dataset_dir), dataset_name="adult")
    
    loader = ResourceLoader(
        resolver=resolver,
        data_loader=DataLoader(),
        dcs_loader=DCsLoader(),
        metadata_loader=MetadataLoader(),
        data_encoder=DataEncoder(),
        dcs_encoder=DCsEncoder()
    )
    
    dataset = loader.load_dataset()
    
    assert dataset.name == "adult"
    assert "workclass" in dataset.data.columns
    assert dataset.data["workclass"].dtype != object  # Encoded
    assert dataset.target == "income"
    assert len(dataset.dcs.constraints) == 1
    
    # Verify DC encoding
    dc = dataset.dcs.constraints[0]
    pred = dc.predicates[0]
    assert pred.left.attr == "workclass"
    assert pred.right.is_value
    # Use a more robust check for encoded literal
    assert str(pred.right.attr).isdigit() or isinstance(pred.right.attr, (int, float))
