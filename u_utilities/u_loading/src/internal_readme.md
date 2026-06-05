# Internal Blueprint: u_loading (RPM Utility)

## Overview
`u_loading` is a standardized ingestion utility for raw datasets, denial constraints, and metadata. It follows the RPM Triad architecture.

## The Triad Split
1.  **Engine (`LoadingResolver`)**: Handles path resolution for a given dataset name and base directory.
2.  **Workers**:
    *   **Loaders (`DataLoader`, `DCsLoader`, `MetadataLoader`)**: Specialized classes for reading specific file formats (CSV, TXT, JSON).
    *   **Encoders (`DataEncoder`, `DCsEncoder`)**: Handles categorical encoding for data and ensuring denial constraints are updated to match encoded values.
3.  **Facade (`ResourceLoader`)**: Orchestrates the loading, sampling, and encoding flow.

## Public API
```python
from u_utilities.u_loading import ResourceLoader, LoadingResolver
from u_utilities.u_loading.src.loaders import DataLoader, DCsLoader, MetadataLoader
from u_utilities.u_loading.src.encoders import DataEncoder, DCsEncoder

# 1. Setup Engine
resolver = LoadingResolver(base_path="data/", dataset_name="adult")

# 2. Setup Workers
workers = {
    "data_loader": DataLoader(),
    "dcs_loader": DCsLoader(),
    "metadata_loader": MetadataLoader(),
    "data_encoder": DataEncoder(),
    "dcs_encoder": DCsEncoder(),
}

# 3. Use Facade
loader = ResourceLoader(resolver=resolver, **workers, sample_size=100)
dataset = loader.load_dataset()
```

## Contracts
- **Input**: Expects a directory (`base/`) containing `original_data.csv`, `dcs.txt`, and `metadata.json`.
- **Output**: Returns a `u_shared.Dataset` object containing encoded data, constraints, and mappings.
