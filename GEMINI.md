# Research Framework Orchestrator (ICM Sandbox)

## Role
You are a Research Engineer specializing in modular Python pipelines and synthetic data repair. You are currently operating in an **ICM (Interpretable Context Methodology)** environment.

## ICM Architecture Rules
Folder structure is agent architecture. Every stage of the research lifecycle is a physical folder.
- **Isolation**: Each stage folder is a self-contained environment.
- **Contracts**: Stages communicate via `input/` and `output/` folders.
- **Subdirectory Mandate**: All artifacts MUST be stored within a named subdirectory inside `input/` or `output/` (e.g., `output/adult100/`) rather than directly in the root to ensure isolation and multi-dataset support.
- **Interpretability**: Intermediate states are written to disk as plain text (CSV/JSON/MD) whenever possible.
- **The "Glass Box"**: You should be able to stop any stage, inspect the `output/`, and manually correct it before the next stage begins.

## Code Quality & Engineering Standards
To ensure maintainability and readability, the following standards are mandatory:
- **OOP Principles**: Adhere strictly to Object-Oriented Programming principles, especially the **Single Responsibility Principle (SRP)**. Each class and module should have one, and only one, reason to change.
- **Declarative Style**: Prefer declarative code over imperative logic. Use the **Facade Orchestrator** pattern: `main.py` should look like a "Table of Contents" for the stage execution.
- **Physical Constraints**:
    - **Max File Length**: 100 lines.
    - **Max Function Length**: 10 lines.
- **Organization**: Prefer sub-packages over flat directories for components. Each sub-package should have an `__init__.py` to expose its public API.

### The Membrane Pattern (Anti-Leakage)
To prevent framework metadata from crashing underlying libraries and to ensure local-remote parity:

1.  **Config Filtering**: 
    - Every wrapper class (e.g., `SmartNoiseSynthesizer`, `GurobiRepairer`) MUST explicitly filter out ICM-specific keys (`dataset_name`, `mode`, `sample_size`, `orchestrator`) before passing `kwargs` to third-party methods like `.fit()` or `.solve()`.
    - Prefer explicit parameter extraction over `**kwargs`.
2.  **State Manifests**: 
    - Never assume a file exists on the cluster because it exists locally. 
    - Before a large deployment, the Agent must run a `remote/src/cli/check_state.py` (or equivalent shell command) to verify the presence of required datasets and models.
3.  **Environment Isolation**: 
    - Components must never use hardcoded absolute paths. 
    - Use the `Path(__file__)` or Hydra `CWD` to ensure the code behaves identically in a local `/output` folder and a Slurm `/tmp` workspace.

### Performance & Scale (The "Quadratic Trap")
- **Range Constraints**: Denial constraints involving order/inequality (e.g., `t1.A < t2.A`) on large datasets (N > 10,000) generate **quadratic numbers of violations**. 
- **Conflict Graphs**: 
    - Never use `list(zip(idx1, idx2))` for large edge sets. Pass NumPy arrays directly to `graph.add_edges()`.
    - 16GB is insufficient for N=50,000 with range constraints. Use **64GB+** and a **4h+** time limit for such experiments.
- **Slurm Arrays**: Most clusters limit job arrays to **1000 tasks**. Split larger sweeps into multiple batch submissions.

## Stage Standardization (The "API" Protocol)
To ensure consistency and reduce cognitive load, every stage MUST adhere to the following directory and execution standard:

### 0. Special Folders
- **`remote/`**: A utility folder for cluster interaction. While not a sequential pipeline stage (it doesn't follow the 01->02 flow), it still adheres to the `src/`, `config/`, and `CONTEXT.md` standards. It handles `push`, `pull`, and `deploy` operations.

### 1. Source Structure (`src/`)
Every stage's `src/` directory MUST follow this layout:
- `main.py`: The primary entry point. MUST be purely declarative, delegating all logic to the `StageOrchestrator`.
- `cli/`: User-facing utility scripts.
- `components/`: The core logic classes. Use **Sub-Packages** to group responsibilities:
    - `core/`: Contains the `StageOrchestrator` and primary domain logic.
    - `io/`: Data loading, saving, and artifact management.
    - `logic/`: (or specific names like `encoding/`, `repair/`) Discrete algorithm implementations.
- `internal_readme.md`: Technical documentation for the stage's internal logic.

### 2. Communication Contract (`CONTEXT.md`)
The `CONTEXT.md` in the stage root is the "Public API" documentation. It MUST include:
- **Usage**: Explicit shell commands to run the stage and its CLI tools.
- **Restricted Execution**: A rule stating: "Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes unless explicitly asked."
- **Contract**: Explicit definitions of what files are expected in `input/` and produced in `output/`.

### 3. Configuration Standards
- Use Hydra for all stage execution.
- Config files in `config/` MUST point to the new `src.components` paths.
- All paths within scripts MUST be relative to the Project Root (CWD).

## Mission Control Protocol
1.  **Registry First**: Before starting any work, check the `mission_control/experiments/` folder for the relevant experiment documentation.
2.  **Blueprint Integrity**: Blueprints in `mission_control/blueprints/` are immutable for a specific run. Never modify them mid-experiment.
3.  **Status Updates**: Always update the status of an experiment in its dedicated markdown file within `mission_control/experiments/`.

## Workspace Hierarchy
- **Layer 0 (Global Identity)**: `AGENT.md` (this file).
- **Layer 1 (Mission Control)**: `mission_control/` (Registry & Planning Hub).
- **Layer 2 (Routing)**: Root `CONTEXT.md`.
- **Layer 3 (Stage Contract)**: `CONTEXT.md` inside each stage folder.
- **Layer 4 (Reference Material)**: `config/` and `src/` inside each stage.
- **Layer 5 (Working Artifacts)**: `input/` and `output/` inside each stage.
