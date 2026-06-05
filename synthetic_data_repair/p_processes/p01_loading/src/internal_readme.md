# p01_loading Internal Documentation: The Glass Box Blueprint

This process handles the initial ingestion of raw datasets into the RPM framework. It transforms external CSV/Metadata into internal `r_resources/r_data/private` artifacts.

## 1. Architectural Triad

### Engine (`LoadingEngine`)
- **Role**: Environment and Path resolution.
- **Logic**: Wraps `ResourceManager` to determine where private data should be stored based on the dataset name.

### Worker (`FileLoader`)
- **Role**: Atomic data transformation.
- **Logic**: 
    1. Loads raw `data.csv`, `dcs.txt`, and `metadata.json` from the source directory.
    2. Performs sampling if `sample_size` is provided.
    3. Encodes categorical variables and updates Denial Constraints accordingly.
    4. Returns a unified `Dataset` entity.

### Facade (`LoadingOrchestrator`)
- **Role**: High-level orchestration and Dependency Injection.
- **Logic**: Coordinates the `Worker` to get the dataset and the `Engine` to find the destination, then performs the save operation.

## 2. Dependency Injection Flow
The `main.py` entry point uses Hydra to instantiate the Triad:
1. `ResourceManager` is injected into `LoadingEngine`.
2. `LoadingEngine` and `FileLoader` are injected into `LoadingOrchestrator`.
3. `orchestrator.run()` is called.

## 3. Contracts
- **Input**: Raw files in a directory (e.g., `data/adult100/`).
- **Output**: RPM-compliant private directory in `r_resources/r_data/adult100/private/`.
