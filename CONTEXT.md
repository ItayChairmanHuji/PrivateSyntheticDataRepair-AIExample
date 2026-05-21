# Pipeline Routing & Overview

This sandbox implements the full research lifecycle for synthetic data repair using the ICM methodology.

## Central Hub
| Name | Responsibility |
| :--- | :--- |
| **[Mission Control](./mission_control/CONTEXT.md)** | Plan experiments, track status, and manage blueprints. |

## Execution Stages
| Stage | Name | Responsibility |
| :--- | :--- | :--- |
| **01** | [Loading](./s01_loading/CONTEXT.md) | Load private datasets and constraints. |
| **02** | [Synthesizing](./s02_synthesizing/CONTEXT.md) | Generate initial synthetic data. |
| **03** | [Marginals Obtaining](./s03_marginals/CONTEXT.md) | Calculate noisy marginals from private/synthetic data. |
| **04** | [Repairing](./s04_repairing/CONTEXT.md) | Apply repair algorithms (e.g., Weighted VC, ILP). |
| **05** | [Evaluating](./s05_evaluating/CONTEXT.md) | Compute metrics and generate JSON results. |
| **06** | [Remote Execution](./s06_remote/CONTEXT.md) | Deploy to Snorlax (Slurm) and monitor jobs. |
| **07** | [Result Syncing](./s07_sync/CONTEXT.md) | Pull results from remote and aggregate them. |
| **08** | [Analysis](./s08_analysis/CONTEXT.md) | Final visualizations and notebook-based analysis. |
| **--** | [Shared](./shared/CONTEXT.md) | Common entities (Dataset, Marginal) and utilities. |

## Execution Workflow
1.  **Define** the experiment in `Mission Control`.
2.  **Generate** the blueprint.
3.  **Execute** the pipeline stages (`01` through `05`).
    - Local: Sequential execution via a master script.
    - Remote: Deploy the "Blueprint" via `06`.
4.  **Retrieve** results in `07`.
5.  **Analyze** in `08`.
