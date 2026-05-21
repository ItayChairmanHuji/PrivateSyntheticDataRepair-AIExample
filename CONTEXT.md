# Pipeline Routing & Overview

This sandbox implements the full research lifecycle for synthetic data repair using the ICM methodology.

## Stage Map
| Stage | Name | Responsibility |
| :--- | :--- | :--- |
| **00** | [Experiment Design](./s00_experiment_design/CONTEXT.md) | Define sweeps and generate experiment blueprints. |
| **01** | [Loading](./01_loading/CONTEXT.md) | Load private datasets and constraints. |
| **02** | [Synthesizing](./02_synthesizing/CONTEXT.md) | Generate initial synthetic data. |
| **03** | [Marginals Obtaining](./03_marginals_obtaining/CONTEXT.md) | Calculate noisy marginals from private/synthetic data. |
| **04** | [Repairing](./04_repairing/CONTEXT.md) | Apply repair algorithms (e.g., Weighted VC, ILP). |
| **05** | [Evaluating](./05_evaluating/CONTEXT.md) | Compute metrics and generate JSON results. |
| **06** | [Remote Execution](./06_remote_execution/CONTEXT.md) | Deploy to Snorlax (Slurm) and monitor jobs. |
| **07** | [Result Syncing](./07_result_syncing/CONTEXT.md) | Pull results from remote and aggregate them. |
| **08** | [Analysis](./08_analysis/CONTEXT.md) | Final visualizations and notebook-based analysis. |
| **--** | [Shared](./00_shared/CONTEXT.md) | Common entities (Dataset, Marginal) and utilities. |

## Execution Workflow
1.  **Plan** the sweep in `00`.
2.  **Execute** the pipeline (`01` through `05`).
    - Local: Sequential execution via a master script or manual handoff.
    - Remote: Deploy the "Blueprint" from `00` via `06`.
3.  **Retrieve** data in `07`.
4.  **Analyze** in `08`.
