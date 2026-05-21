---
name: icm-pipeline-developer
description: Specialized guidance for developing modular pipeline stages in the ICM architecture. Use when adding new loading, synthesizing, or repairing algorithms to the research framework.
---

# ICM Pipeline Developer

This skill guides you through implementing and testing new modular stages within the ICM (Interpretable Context Methodology) framework.

## Core Principles
- **Stage Isolation**: A stage must never import code from another stage. Only import from `00_shared/`.
- **File-based Handoff**: Each stage reads from `input/` and writes to `output/`.
- **10-Line Rule**: Functions should ideally be ~10 lines long, following the single responsibility principle.

## Workflow: Adding a New Algorithm
1.  **Identify the Stage**: Determine where the algorithm fits (e.g., a new repairer goes to `04_repairing`).
2.  **Define the Config**: Create a Hydra YAML in the stage's `config/` folder using the `_target_` pattern.
3.  **Implement the Class**: Write the logic in `src/`. Ensure it inherits from the appropriate base class in `00_shared/entities/`.
4.  **Create a Main Script**: Each stage needs a `main.py` that handles Hydra instantiation and file I/O.
5.  **Verify with Notebook**: Create a test notebook in `tests/` to visualize the algorithm's performance on a small sample.

## Troubleshooting
- **Input Errors**: Check if the previous stage's `output/` matches the expected format in this stage's `CONTEXT.md`.
- **Entity Mismatch**: Ensure all data is wrapped in `Dataset` or `MarginalSet` objects before processing.
