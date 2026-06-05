# Synthetic Data Repair Framework (RPM Architecture)

This is the next-generation architecture for the synthetic data repair research framework. It replaces the previous stage-based ICM model with a more scalable and granular approach.

## Structure

- **`p_processes/`**: The functional entry points (Verbs).
- **`r_resources/`**: The centralized, parameter-driven state (State).
- **`u_utilities/`**: The shared, atomic logic packages (Tools).
- **`mission_control/`**: Experiment blueprints and results registry.

## Quick Start

### 1. Load a Dataset
```bash
python -m p_processes.p01_loading.main dataset_name=adult100
```

### 2. Train a Model
```bash
python -m p_processes.p02_synthesizing.p02a_training.main dataset_name=adult100 epsilon=0.1
```

### 3. Run a Sweep
```bash
python -m p_processes.p02_synthesizing.p02a_training.main --multirun dataset_name=adult100 epsilon=0.1,1.0,10.0
```

## Documentation

- [NEW_ARCHITECTURE.md](NEW_ARCHITECTURE.md): The architectural vision and rationale.
- [REPOSITORY_RULES.md](REPOSITORY_RULES.md): The mandatory rules for development.
- [GEMINI.md](GEMINI.md): Instructions for the AI Research Engineer (Agent).
