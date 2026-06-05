# Utility: u_loading

## Purpose
Handles data ingestion, type inference, and categorical encoding for raw datasets.

## Interface
- **`DataLoader`**: Standardized loading from CSV.
- **`Encoders`**: One-hot and label encoders for categorical attributes.

## Usage
```python
from u_utilities.u_loading import ResourceLoader, LoadingResolver
from u_utilities.u_loading.src.loaders import DataLoader, DCsLoader, MetadataLoader
from u_utilities.u_loading.src.encoders import DataEncoder, DCsEncoder

resolver = LoadingResolver(base_path="data/", dataset_name="adult")
loader = ResourceLoader(
    resolver=resolver,
    data_loader=DataLoader(),
    dcs_loader=DCsLoader(),
    metadata_loader=MetadataLoader(),
    data_encoder=DataEncoder(),
    dcs_encoder=DCsEncoder()
)
dataset = loader.load_dataset()
```
