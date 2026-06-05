# p01_loading Internal Documentation: The Process Triad Blueprint

This process handles the initial ingestion of raw datasets into the RPM framework. It transforms external CSV/Metadata into internal `r_resources/r_data/private` artifacts.

## 1. The Process Triad

### Engine (`LoadingEngine`)
- **Role**: Resource Interaction.
- **Logic**: Interacts with `r_resources` via the `ResourceManager`. It handles the "Where" (resolving private data directories and saving datasets).

### Logic (`LoadingCore`)
- **Role**: Core Math and Transformations.
- **Logic**: 
    1. Loads raw `original_data.csv`, `dcs.txt`, and `metadata.json` from the source directory.
    2. Performs sampling if `sample_size` is provided.
    3. Encodes categorical variables and updates Denial Constraints accordingly.
    4. Returns a unified `Dataset` entity.

### Orchestrator (`LoadingWorker`)
- **Role**: High-level Coordination.
- **Logic**: The central hub that uses Dependency Injection (DI) to connect the `Engine` and `Logic`. It coordinates the loading flow and saves the final result.

## 2. Dependency Injection Flow
The `main.py` entry point uses Hydra to instantiate the Triad:
1. `ResourceManager` is injected into `LoadingEngine`.
2. `LoadingEngine` and `LoadingCore` are injected into `LoadingWorker`.
3. `worker.run()` is called.

## 3. Contracts
- **Input**: Raw files in a directory (e.g., `data/adult100/base/`).
- **Output**: RPM-compliant private directory in `r_resources/r_data/adult100/private/`.
