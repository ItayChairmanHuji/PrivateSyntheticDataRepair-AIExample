# Source Code Overview

This directory contains the core implementation of the research framework for repairing synthetic data using marginals from private data.

## System Architecture

The system follows a modular pipeline design, where each stage is independent and replaceable. This modularity is managed through an orchestration pattern and Hydra-based configurations.

### Pipeline Stages

1. **[Loading](./loading/CONTEXT.md)**: Responsible for reading private datasets, metadata, and constraints. It ensures data consistency and handles initial processing.
2. **[Synthesizing](./synthesizing/CONTEXT.md)**: Generates synthetic data from the private data. Different synthesis methods can be swapped here.
3. **Marginals Obtaining**: Calculates and extracts noisy marginals from both private and synthetic data.
4. **Repairing**: The core logic that uses obtained marginals to improve the quality of the synthetic data.
5. **Evaluating**: Aggregates results from all previous stages and computes metrics to assess the repair's effectiveness.

## Core Directories

- `entities/`: Contains common data structures and classes used across multiple stages (e.g., `Dataset`, `MarginalSet`, `ExperimentResult`).
- `utils/`: Shared helper functions for logging, data manipulation, or generic mathematical operations.
- `.../`: Each stage has its own directory containing its specific logic and implementation.

## Development Standards

- **Modularity**: Ensure that each stage implementation can be swapped without breaking others.
- **Testing**: Each implementation should be verified with a corresponding tests script in the `/tests` directory. **A test MUST be created or updated for every new feature to ensure no regressions.**
- **Hydra Integration**: All stages should be configurable via the `/config` directory.
- **Documentation Parity**: If you modify any code, implementation, or configuration, you MUST update the corresponding `.md` files (e.g., `CONTEXT.md`, `AGENT.md`) to reflect the changes.
- **Clean code and OOP**: Make sure to follow the clean code OOP ideas to make the code clean and readable. 
- **Orchestration Pattern**: Try to use an orchestration pattern when possible- classes that have logic and classes that combines these classes together. Try to avoid combining the classes. 
- **File/function sizes**: As a thumb rule, a file should NOT be beyond ~100 lines and a function shouldn't be beyond ~10 lines.
- **Documentation**: The code should be self explanatory, meaning that comments are not needed to understand to understand the code and the flow of the process. For extremely complicated logic, comments are allowed, but this is the only case.
- **Imports**: Imports that are not used in a file should not be in the file. 
- **Single Responsibility**: A class and a function should have a single responsibility, when one becomes too complicated consider to split the logic into multiple classes/functions. This is strongly related to the orchestration pattern. 


## Development Workflows

### Applying Hydra-Configurator
When adding a new component or stage:
1. Define the implementation in `src/`.
2. Create a corresponding YAML configuration in `config/` using the orchestration pattern (`_target_`).
3. Ensure the configuration fully defines the runtime object without requiring hardcoded logic in the orchestration layer.
4. Implement tests in the `tests/` directory to make sure nothing was broken and the new feature/bugfix works. 

### Applying Research-Notebook-Validator
Before finalizing any implementation:
1. Create a notebook in `notebooks/` named `test_<implementation_name>.ipynb`.
2. Implement **Logical Tests** to verify edge cases and core logic.
3. Add **Visualizations** (using matplotlib/seaborn) to show the data transformations.
4. Run a **Runtime Test** to ensure the implementation is efficient enough for research experiments.