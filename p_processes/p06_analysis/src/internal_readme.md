# p06_analysis Internal Documentation: The Glass Box Blueprint

This process aggregates evaluation JSON results from multiple experiments and generates summarized metrics, CSV tables, and plots.

## 1. Architectural Triad

### Engine (`AnalysisEngine`)
- **Role**: Path resolution for reading raw results and saving summarized output.
- **Logic**: Wraps `ResourceManager` to resolve paths for `r_resources/r_results/` (input) and `r_resources/r_analysis/` (output).

### Worker (`AnalysisWorker`)
- **Role**: Summarization and plotting logic.
- **Logic**: Delegates the data aggregation and visualization to a Hydra-instantiated `analyzer`.

### Facade (`AnalysisOrchestrator`)
- **Role**: Coordinates the pipeline.
- **Logic**: Uses the engine to locate all JSON artifacts for a given `experiment_id`, loads them into a list, creates the target analysis directory, and passes everything to the worker.

## 2. Dependency Injection Flow
1. `ResourceManager` is injected into `AnalysisEngine`.
2. A configured `analyzer` is injected into `AnalysisWorker`.
3. `AnalysisEngine` and `AnalysisWorker` are injected into `AnalysisOrchestrator` along with the configuration (`experiment_id`, `timestamp`).
4. `main.py` invokes `orchestrator.run()`.

## 3. Contracts
- **Input**: Multiple evaluation JSON files located at `r_resources/r_results/{experiment_id}/...`.
- **Output**: Aggregated data and plots located at `r_resources/r_analysis/{experiment_id}/...`.
