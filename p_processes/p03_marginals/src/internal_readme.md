# p03_marginals Internal Documentation: The Process Triad Blueprint

This process handles the calculation of target marginals for a dataset, which are used for evaluating utility and guiding repair.

## 1. The Process Triad

### Engine (`MarginalsEngine` in `src/engine.py`)
- **Role**: Resource Gateway.
- **Logic**: Interacts with `r_resources` via the `ResourceManager`. It handles the "Where" (loading datasets and saving marginals).

### Logic (`MarginalsCore` in `src/core/`)
- **Role**: Core Math and Transformations.
- **Logic**: Calculates 2-way marginals involving the target attribute. Can add noise for differential privacy.

### Orchestrator (`MarginalsWorker` in `src/worker.py`)
- **Role**: High-level Coordination.
- **Logic**: The central hub that uses Dependency Injection (DI) to connect the `Engine` and `Logic`. It coordinates the calculation flow: Load Dataset -> Calculate -> Save.

## 2. Dependency Injection Flow
1. `ResourceManager` is injected into `MarginalsEngine`.
2. `MarginalsEngine` and `MarginalsCore` are injected into `MarginalsWorker` along with configuration parameters (`dataset_name`, `noise_level`).
3. `main.py` invokes `worker.run()`.

## 3. Contracts
- **Input**: The private dataset at `r_resources/r_data/...`.
- **Output**: A generated JSON at `r_resources/r_marginals/...`.
