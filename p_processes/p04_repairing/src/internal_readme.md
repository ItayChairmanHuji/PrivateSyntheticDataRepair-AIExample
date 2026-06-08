# Repairing Process (Internal)

This process group handles the repair of synthetic datasets to satisfy integrity constraints (DCs) while maintaining statistical utility.

## Architecture

Following the RPM Triad:

1.  **Engine (`engine.py`)**: Handles the "Where". It uses the `ResourceManager` to resolve paths for synthetic datasets, marginals, and the final repaired output.
2.  **Worker (`worker.py`)**: Handles the "When". It orchestrates the loading of data via the Engine, the execution of the repair logic via the injected Core repairer, and the saving of the results.
3.  **Core (`src/core/`)**: Handles the "How". Contains the specialized graph structures and repair algorithms.

## Usage

Each sub-process (e.g., `p04a_vanilla_repairing`) uses the common Worker and Engine but injects a different Repairer implementation via Hydra.
