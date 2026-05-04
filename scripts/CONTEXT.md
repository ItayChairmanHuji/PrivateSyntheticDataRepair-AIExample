# Research Scripts

This directory contains scripts for running experiments, benchmarking components, and collecting results.

## Key Scripts

### Experiment Execution
- `slurm_manager.py`: Manages the lifecycle of experiments on a remote Slurm cluster. Supports:
    - `push`: Sync code and update requirements on the remote.
    - `submit`: Submit a group of experiments to Slurm (supports naming and file-based overrides).
    - `status`: Check the status of active and recent jobs.
    - `pull`: Retrieve results and logs via rsync/scp (supports pulling by group name).
    - `logs`: Tail the output and error logs of a job.
    - `clean`: Remove results and logs from the remote server.
- `run_parallel_experiments.py`: A helper script used on both local and remote to run multiple Hydra experiments in parallel within a single process/job.
- `launch_experiments.py`: A script to programmatically generate and launch large experiment grids.

### Result Collection & Analysis
- `aggregate_results.py`: Aggregates all JSON result files from the `results/` directory into a single `experiment_results_summary.csv` for analysis.

### Benchmarking & Testing
- `benchmark_violation_finder.py`: Measures the performance of the `ViolationFinder` on large datasets.
- `benchmark_census_logic.py`: Specifically benchmarks the logic used for Census data.
- `compare_engines.py`: Compares the performance of Pandas vs. DuckDB for violation finding.
- `test_new_finder.py`: Validation script for the optimized `ViolationFinder`.
- `test_synthetic_violations.py`: Tests the detection of synthetically injected violations.

## Remote Slurm Workflow
1.  **Configure**: Set remote host and Slurm defaults in `config/remote/slurm.yaml`.
2.  **Push**: `python scripts/slurm_manager.py push`
3.  **Submit**: `python scripts/slurm_manager.py submit "experiment=adult_weighted" "experiment=census_weighted" --name my_experiment_group`
4.  **Status**: `python scripts/slurm_manager.py status`
5.  **Pull**: `python scripts/slurm_manager.py pull --name my_experiment_group`
6.  **Analyze**: `python scripts/aggregate_results.py`

## Workflow
1. Use `main.py` with Hydra overrides or `experiment=...` to run specific configurations.
2. Use `slurm_manager.py` for remote execution on the Snorelax cluster.
3. Use `aggregate_results.py` to compile findings into a CSV.
