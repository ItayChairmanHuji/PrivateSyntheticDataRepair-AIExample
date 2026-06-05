# p04_repairing Internal Documentation: The Glass Box Blueprint

This process handles repairing synthetic data to satisfy Denial Constraints while maintaining utility measured by target marginals.

## 1. Architectural Triad

### Engine (`RepairingEngine`)
- **Role**: Path resolution for reading synthetic data, marginals, and saving repaired data.
- **Logic**: Wraps `ResourceManager` to resolve these paths strictly based on configured parameters.

### Worker (`RepairingWorker`)
- **Role**: Data repair logic.
- **Logic**: Delegates the repair operation to a `repairer` component (e.g. `VanillaVCRepairer`, `WeightedVCRepairer`) initialized by Hydra. 

### Facade (`RepairingOrchestrator`)
- **Role**: Coordinates the pipeline.
- **Logic**: Uses the engine to find/load the private dataset (for metadata/constraints), synthetic dataset, and target marginals. Calls the worker to repair the data, and finally saves the repaired CSV to the parameter-driven path via the engine.

## 2. Dependency Injection Flow
1. `ResourceManager` is injected into `RepairingEngine`.
2. A configured `repairer` is injected into `RepairingWorker`.
3. `RepairingEngine` and `RepairingWorker` are injected into `RepairingOrchestrator` along with configuration parameters (`dataset_name`, `synthesizer_name`, `repairer_name`, `epsilon`, `seed`, `size`, `noise_level`, `alpha`).
4. `main.py` invokes `orchestrator.run()`.

## 3. Contracts
- **Input**: Synthetic dataset at `r_resources/r_data/synthetic/...` and marginals at `r_resources/r_marginals/...`.
- **Output**: Repaired dataset at `r_resources/r_data/repaired/...`.
