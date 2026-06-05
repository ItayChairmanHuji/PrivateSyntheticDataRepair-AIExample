# Process: p01_loading

## Purpose
Initializes the framework by loading raw datasets into the `r_resources/r_data/private/` area. This process bridges the external data sources and the internal RPM resource hierarchy.

## Architectural Triad
- **Engine (`LoadingEngine`)**: Resolves physical storage paths using the `ResourceManager`.
- **Worker (`FileLoader`)**: Orchestrates the atomic loading, sampling, and categorical encoding of raw artifacts.
- **Facade (`LoadingWorker`)**: Coordinates the engine and worker to execute the end-to-end ingestion flow.

## Contract
- **Input**: Raw CSV/Metadata from external source (e.g., `data/{dataset_name}/`).
- **Output**: `r_resources/r_data/private/{dataset_name}/data.csv`
- **Output**: `r_resources/r_data/private/{dataset_name}/metadata.json`
- **Output**: `r_resources/r_data/private/{dataset_name}/dcs.txt`

## Usage
```bash
# Run for the default dataset (adult100)
python -m p_processes.p01_loading.main

# Run for a specific dataset
python -m p_processes.p01_loading.main --config-name loading/adult
```
