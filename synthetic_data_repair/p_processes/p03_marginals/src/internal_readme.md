# p03_marginals Internal Documentation: The Glass Box Blueprint

This process handles the calculation of target marginals for a dataset, which are used for evaluating utility and guiding repair.

## 1. Architectural Triad

### Engine (`MarginalsEngine`)
- **Role**: Path resolution for saving marginals.
- **Logic**: Wraps `ResourceManager` to resolve marginal output paths based on configured parameters.

### Worker (`MarginalsWorker`)
- **Role**: Marginal calculation logic.
- **Logic**: Delegates the calculation to a `calculator` (e.g. `TopKMarginalsCalculator`) initialized by Hydra.

### Facade (`MarginalsOrchestrator`)
- **Role**: Coordinates the pipeline.
- **Logic**: Extracts parameters, uses the engine to find and load the private dataset, calls the worker to calculate marginals, and finally saves the marginals to the parameter-driven path via the engine.

## 2. Dependency Injection Flow
1. `ResourceManager` is injected into `MarginalsEngine`.
2. A configured `calculator` is injected into `MarginalsWorker`.
3. `MarginalsEngine` and `MarginalsWorker` are injected into `MarginalsOrchestrator` along with configuration parameters (`dataset_name`, `noise_level`).
4. `main.py` invokes `orchestrator.run()`.

## 3. Contracts
- **Input**: The private dataset at `r_resources/r_data/...`.
- **Output**: A generated JSON at `r_resources/r_marginals/...`.
