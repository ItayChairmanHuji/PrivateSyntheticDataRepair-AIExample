# Research Notebooks

This directory contains Jupyter notebooks used to test and validate individual stage implementations.

## Naming Convention
- `test_<implementation_name>.ipynb`

## Standards (Research-Notebook-Validator)
Each code block should be relatively short, so code would be readable. 
Include markdowns to explain what is done in test.
Every notebook must include the following sections to be considered valid:

### 1. Logical Tests
- Small-scale tests with known inputs and expected outputs.
- Verification of edge cases (e.g., empty datasets, single-column marginals).
- Assertion-based checks to ensure algorithmic correctness.

### 2. Visualization
- Comparative plots (e.g., private vs. synthetic data distributions).
- Tables showing marginal counts or error metrics.
- Visual proof that the "repair" is actually improving the data.

### 3. Runtime Test
- Execution time measurements for the main logic.
- Assessment of scalability with respect to data size.

## Notebook Descriptions
- `test_co_noise.ipynb`: Validates the `CoNoise` synthesizer logic.
- `test_evaluating.ipynb`: Tests the evaluation orchestrator and individual evaluators.
- `test_file_loader.ipynb`: Validates the data and DC loading process.
- `test_marginals_obtaining.ipynb`: Validates the extraction of noisy marginals.
- `test_repairing.ipynb`: Tests the data repair strategies (ILP, VC).
- `test_violation_finder.ipynb`: Validates the `ViolationFinder` component.
- `test_slurm_manager.ipynb`: Validates the remote Slurm execution manager logic.
- `optimize_violation_finder.ipynb`: Benchmarks and optimizes the violation finding logic.

## Analysis & Visualization
- `alpha_eps01_b1000_analysis.ipynb`: Specifically analyzes the alpha sweep with eps=0.1 and near-perfect marginals (budget=1000), providing a baseline for the theoretical best repair performance.
- `alpha_sweep_analysis.ipynb`: Visualizes the results of the alpha sweep experiments, showing the impact of the repair parameter on data utility.
- `final_experiment_analysis.ipynb`: Comprehensive analysis of the final research experiments.
- `weighted_vc_alpha_eps01_analysis.ipynb`: Analysis specifically for the weighted VC algorithm under eps=0.1.
- `weighted_vc_may15_analysis.ipynb`: Analysis for experiments conducted on May 15th.
- `weighted_vc_may2026_analysis.ipynb`: Current state analysis for the May 2026 experiments.
