# Shared Entities and Utilities

## Purpose
Provides the foundational building blocks used by all stages of the pipeline to ensure consistency and type safety.

## Contents
- **entities/**: Python classes for `Dataset`, `Marginal`, `Constraint`, and `ExperimentResult`.
- **utils/**: Helper functions for I/O, DP mechanisms, logging, and Hydra integration.

## Usage
- **Tests**: Run `pytest shared/tests/test_shared.py` to verify the core components.

## Stage Rules
- Avoid adding stage-specific logic here. This folder should only contain code that is truly generic or shared by 3+ stages.
- All entities should be serializable.
- Adhere strictly to the 100/10 rule (Max 100 lines per file, Max 10 lines per function).
- Every public API must be exposed in `__init__.py`.
