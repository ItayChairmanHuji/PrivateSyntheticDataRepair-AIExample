# Shared Entities and Utilities

## Purpose
Provides the foundational building blocks used by all stages of the pipeline to ensure consistency and type safety.

## Contents
- **entities/**: Python classes for `Dataset`, `Marginal`, `Constraint`, and `ExperimentResult`.
- **utils/**: Helper functions for I/O, DP mechanisms, logging, and Hydra integration.

## Stage Rules
- Avoid adding stage-specific logic here. This folder should only contain code that is truly generic or shared by 3+ stages.
- All entities should be serializable (e.g., via `pydantic` or `json`).
