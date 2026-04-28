# Research Scripts

This directory contains scripts for running experiments, benchmarking components, and collecting results.

## Key Scripts

### Experiment Execution
- `run_parallel_experiments.py`: Runs multiple research experiments in parallel using a `ProcessPoolExecutor`. Supports a configurable worker limit.
- `slurm_manager.py`: Manages the lifecycle of experiments on a remote Slurm cluster. Supports pushing code, submitting jobs, checking status, and pulling results/logs.
- `run_adult_experiments.bat`: Runs the full suite of experiments for the Adult dataset using various repair algorithms.
- `run_adult5000_experiments.bat`: Similar to the above, but specifically for a 5000-row subset.

### Remote Slurm Workflow
To run experiments on a remote cluster:
1.  **Configure**: Set remote host and Slurm defaults in `config/remote/slurm.yaml`.
2.  **Push**: Run `python scripts/slurm_manager.py push` to sync code to the server.
3.  **Submit**: Run `python scripts/slurm_manager.py submit "loading.name=adult" "loading.name=compas"` to queue jobs.
4.  **Status**: Run `python scripts/slurm_manager.py status` to check progress.
5.  **Pull**: Run `python scripts/slurm_manager.py pull` and `python scripts/slurm_manager.py logs` to retrieve results and logs once jobs are done.

### Result Collection
- `collect_results_full.py`: Aggregates results from multiple experiment runs into a summary table.
- `collect_results.py`: A simpler version of result collection.

### Benchmarking
- `benchmark_violation_finder.py`: Measures the performance of the `ViolationFinder` on large datasets.
- `benchmark_census_logic.py`: Specifically benchmarks the logic used for Census data.
- `benchmark_large.py`: General performance benchmark for large data.
- `benchmark_noisy_datasets.py`: Benchmarks performance when varying noise levels.

### Utility & Testing
- `compare_engines.py`: Compares the performance of Pandas vs. DuckDB for violation finding.
- `inspect_compas_violations.py`: Utility to inspect violations in the COMPAS dataset.
- `test_new_finder.py`: Validation script for the optimized `ViolationFinder`.
- `test_synthetic_violations.py`: Tests the detection of synthetically injected violations.

## Workflow
1. Use `main.py` with Hydra overrides to run specific configurations.
2. Use `.bat` files to run batches of experiments.
3. Use `collect_results_full.py` to view the summary of findings.
