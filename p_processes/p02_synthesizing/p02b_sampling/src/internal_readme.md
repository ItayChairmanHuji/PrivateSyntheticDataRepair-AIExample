# p02b_sampling Internal Documentation: The Glass Box Blueprint

This process handles the generation of synthetic data from a pre-trained model artifact.

## 1. Architectural Triad

### Engine (`SamplingEngine`)
- **Role**: Path resolution for reading models and saving synthetic data.
- **Logic**: Wraps `ResourceManager` to resolve model and synthetic data paths strictly based on configured parameters.

### Worker (`SamplingWorker`)
- **Role**: Data generation core.
- **Logic**: Delegates the generation to a `sampler` (e.g. `SmartNoiseSynthesizer`) initialized by Hydra.

### Orchestrator (`SamplingWorker`)
- **Role**: Coordinates the pipeline.
- **Logic**: Extracts parameters, uses the engine to find/load the private dataset (for metadata) and the model, calls the worker to sample data, and finally saves the synthetic data to the parameter-driven path via the engine.

## 2. Dependency Injection Flow
1. `ResourceManager` is injected into `SamplingEngine`.
2. A configured `sampler` is injected into `SamplingWorker`.
3. `SamplingEngine` and `SamplingWorker` are injected into `SamplingWorker` along with configuration parameters (`dataset_name`, `engine_name`, `epsilon`, `seed`, `size`).
4. `main.py` invokes `worker.run()`.

## 3. Contracts
- **Input**: A trained model pickle file at `r_resources/r_models/...` and the private dataset at `r_resources/r_data/...`.
- **Output**: A generated CSV at `r_resources/r_data/synthetic/...`.
