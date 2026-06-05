# p05_evaluating Internal Documentation: The Glass Box Blueprint

This process handles evaluating the quality of synthetic and repaired data, generating metrics like utility (marginal error) and privacy.

## 1. Architectural Triad

### Engine (`EvaluatingEngine`)
- **Role**: Path resolution for reading private, synthetic, and repaired datasets, as well as saving the evaluation JSON results.
- **Logic**: Wraps `ResourceManager` to resolve these paths based on configured parameters.

### Worker (`EvaluatingWorker`)
- **Role**: Metric calculation logic.
- **Logic**: Delegates the evaluation to a Hydra-instantiated `evaluator` (or an orchestrator of multiple evaluators, like `EvaluationOrchestrator`) which computes metrics over a `PipelineResult` object.

### Facade (`EvaluatingOrchestrator`)
- **Role**: Coordinates the pipeline.
- **Logic**: Uses the engine to locate all necessary artifacts, builds a combined `PipelineResult` entity, calls the worker to generate a metrics dictionary, and saves the final JSON report to the parameter-driven path.

## 2. Dependency Injection Flow
1. `ResourceManager` is injected into `EvaluatingEngine`.
2. A configured `evaluator` is injected into `EvaluatingWorker`.
3. `EvaluatingEngine` and `EvaluatingWorker` are injected into `EvaluatingOrchestrator` along with all necessary configuration parameters to resolve artifact paths.
4. `main.py` invokes `orchestrator.run()`.

## 3. Contracts
- **Input**: The full stack of previously generated resources (`r_data/private`, `r_data/synthetic`, `r_data/repaired`).
- **Output**: Evaluation results as JSON at `r_resources/r_results/...`.
