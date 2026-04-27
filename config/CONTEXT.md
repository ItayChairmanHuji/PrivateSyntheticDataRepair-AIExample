# Configuration Management

This directory contains the Hydra configuration files for the research framework.

## Structure
Configurations are organized into groups corresponding to the pipeline stages:
- `loading/`: Configurations for data loading implementations.
- `synthesizing/`: Configurations for synthetic data generation.
- `marginals_obtaining/`: Configurations for marginal extraction.
- `repairing/`: Configurations for data repair algorithms.
- `evaluating/`: Configurations for evaluation metrics.

## Standards (Hydra-Configurator)
1. **Orchestration Pattern**: Every configuration should define a `_target_` field pointing to the Python class to be instantiated.
2. **Modular Swappability**: Ensure that changing a config file (or passing a different one via command line) is sufficient to swap an entire stage implementation.
3. **Parameterization**: All hyperparameters and file paths should be defined here, never hardcoded in the source code.
4. **Experiments Pattern**: A standard pattern when using hydra, a single experiment file that combines multiple components.