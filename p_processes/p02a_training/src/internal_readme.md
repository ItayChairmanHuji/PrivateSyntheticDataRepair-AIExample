# Internal Readme: p02a_training (The Glass Box)

## Overview
The `p02a_training` process is responsible for training generative models (Synthesizers) on private datasets. It follows the RPM Architectural Triad to ensure separation of concerns and testability.

## Architectural Triad

### 1. The Engine (`src/engines/training_engine.py`)
- **Responsibility**: Path resolution and interaction with `r_resources`.
- **Logic**: Uses `ResourceManager` to resolve model saving paths and load private datasets.
- **Key Methods**:
    - `get_model_path()`: Resolves the parameter-driven path for the model.
    - `load_dataset()`: Loads the private dataset.
    - `save_model()`: Persists the trained model.

### 2. The Worker (`src/workers/training_worker.py`)
- **Responsibility**: Atomic training logic.
- **Logic**: Takes a `trainer` (instantiated via Hydra) and a `Dataset` object, and calls the training method.
- **Key Methods**:
    - `train()`: Executes the synthesizer's training routine.

### 3. The Facade (`src/facades/training_facade.py`)
- **Responsibility**: Orchestration.
- **Logic**: Coordinates the Engine and Worker. It loads data, triggers training, and saves the resulting model.
- **Key Methods**:
    - `run()`: The main orchestration entry point.

## Data Flow
1. `main.py` instantiates the `TrainingFacade`.
2. Facade calls `Engine.load_dataset()`.
3. Facade calls `Worker.train()`.
4. Facade calls `Engine.get_model_path()` to find the destination.
5. Facade calls `Engine.save_model()`.

## Configuration
All configuration is handled via Hydra. The process uses a resilient accessor pattern to support both flat and nested configurations.
