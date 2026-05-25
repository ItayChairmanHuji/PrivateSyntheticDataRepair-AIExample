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
- **OOP & Dataclasses**: Adhere strictly to SRP. Prefer `dataclasses` for components that primarily hold state or configuration to keep constructors clean and boilerplate-free.
- **Declarative Style**: Use the **Facade Orchestrator** pattern. `main.py` should look like a "Table of Contents" for the stage execution.
- **Physical Constraints**:
    - **Max File Length**: 100 lines.
    - **Max Function Length**: 10 lines.
- **Documentation & Comments**: 
    - **No Trivial Comments**: Do not comment on what is obvious from the code (e.g., `# Initialize class`).
    - **High-Signal Comments**: Only use comments to explain "Why" or complex "How" that isn't immediately clear from the variable/function names.
- **Structural Consistency**: Adhere strictly to the **Hybrid (Theme/Domain)** split. Each sub-package MUST have an `__init__.py` to expose its public API.

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
6.  **Optimized Syncing**:
    - The `remote/src/remote/pusher.py` MUST exclude large artifacts (`data/`, `outputs/`, `models/`, `remote/output/`) by default to ensure fast code synchronization.
    - Large data transfers should be handled via targeted `paths` parameter or manual cluster commands.
7.  **Dataset Subset Resolution**:
    - Orchestration scripts (like `runner.py`) MUST be robust to dataset subsets (e.g., `adult100`, `census1000`).
    - If a specific model folder for a subset is missing, the script SHOULD attempt to resolve to the base dataset (e.g., stripping numeric suffixes) to allow reusing pre-trained models.

## The Performance Pact (Zero-Waste Research)
To ensure that getting results from the server and analyzing them remains near-instant:

1.  **Lightweight Pulling (The 90/10 Rule)**:
    - ALWAYS use `stats_only=true` when pulling results from large sweeps (> 100 jobs). 
    - This retrieves only the 1KB `.json` evaluation files rather than the 50MB `.csv` datasets, reducing transfer time by 98%.
2.  **Automated Flattening**:
    - Stage 06 MUST use the `ResultFlattener` component to transform nested remote artifacts into flat analysis-ready CSVs during the orchestration phase.
    - Manual preprocessing scripts are forbidden; all logic must reside in `src/io/result_flattener.py`.
3.  **Result Registry**:
    - The `remote` stage SHOULD maintain a `remote/output/registry.json` manifest that maps `job_id` to its completion status to avoid redundant zipping/pulling of existing results.
4.  **Standardized Plotting (The Research Split)**:
    - All analysis plots MUST be split by `dataset` (separate figures or subplots).
    - `hue` MUST represent `repair_algorithm`.
    - `style` (markers/dashes) MUST represent the `synthesizer` (generation algorithm).
    - Synthetic baselines MUST be plotted as reference lines or distinct points, clearly separated by synthesizer.
    - Graph evolution (Alpha, Hubbiness, Connectivity) MUST be plotted both against `epsilon` and across `iterations`.

### Performance & Scale (The "Quadratic Trap")
- **Range Constraints**: Denial constraints involving order/inequality (e.g., `t1.A < t2.A`) on large datasets (N > 10,000) generate **quadratic numbers of violations**. 
- **Conflict Graphs**: 
    - Never use `list(zip(idx1, idx2))` for large edge sets. Pass NumPy arrays directly to `graph.add_edges()`.
    - 16GB is insufficient for N=50,000 with range constraints. Use **64GB+** and a **4h+** time limit for such experiments.
- **Slurm Arrays**: Most clusters limit job arrays to **1000 tasks**. Split larger sweeps into multiple batch submissions.
- **Remote Pulling (Scale)**: When pulling results for sweeps with **> 100 jobs**, ALWAYS use the `stats_only=true` flag. Pulling raw data (CSV/Pickle) at this scale causes SSH timeouts and zipping overhead that can crash login nodes.

## Stage Standardization (The "API" Protocol)
To ensure consistency and reduce cognitive load, every stage MUST adhere to the following directory and execution standard:

### 0. Special Folders
- **`remote/`**: A utility folder for cluster interaction. While not a sequential pipeline stage (it doesn't follow the 01->02 flow), it still adheres to the `src/`, `config/`, and `CONTEXT.md` standards. It handles `push`, `pull`, `deploy`, and `rerun` operations.

### 1. Source Structure (`src/`)
Every stage's `src/` directory MUST follow this layout to ensure maximum discoverability and separation of concerns:

- **Plumbing (Theme-Based)**: Standardized across all stages.
    - `orchestration/`: Contains the `StageOrchestrator` (the Facade/Brain).
    - `io/`: Contains the stage-level orchestration of files (`FileLoader`, `ArtifactSaver`) and CLI tools (`clean.py`).
    - `loaders/`: Contains low-level format loaders (e.g., `DataLoader`, `DCsLoader`).
- **Domain (Specific Logic)**: Named after the stage's research responsibility.
    - `[DomainName]/`: (e.g., `encoders/`, `synthesizers/`, `repairers/`) Contains the core algorithms, split into individual files per component.

- `main.py`: The purely declarative entry point.
- `internal_readme.md`: Technical documentation for the stage's internal logic.

## Stage Validation Standards
Every stage MUST have a comprehensive test suite in its `tests/` directory (e.g., `test_stage.py`) that satisfies the following conditions:
1. **API Coverage**: The tests MUST execute and verify all public API commands documented in the stage's `CONTEXT.md` (e.g., `main.py`, `clean.py`, `list_datasets.py`).
2. **Orchestration Validation**: The tests MUST run the full orchestration flow via the `StageOrchestrator` using a mock or dummy dataset to ensure all components are correctly wired.
3. **Automated Verification**: All tests MUST pass before a stage is considered "ready".

### Agent Refactoring Checklist (The "Gold Standard")
When refactoring a stage (02-06), follow this checklist to ensure compliance:
1. **Flatten Structure**: Remove `components/` and `cli/`. Promote themes to top-level `src/`.
2. **Standard Themes**: Create/Move code into `orchestration/`, `io/`, and `loaders/`.
3. **Domain Domain**: Create a folder named after the stage's logic (e.g., `synthesis/`, `repair/`).
4. **Clean Exports**: Every sub-package MUST have an `__init__.py` exposing its API.
5. **Dataclass Components**: Convert state-holding components to `@dataclass`.
6. **Silent Code**: Remove all trivial/boilerplate comments.
7. **Declarative Main**: `main.py` should only instantiate and run the `StageOrchestrator`.
8. **100/10 Rule**: No file > 100 lines, no function > 10 lines.
9. **Full Coverage**: Create `tests/test_stage.py` verifying all API commands and the Orchestrator.
10. **Reference**: Use **Stage 01 (`s01_loading`)** as the physical example of this standard.

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
