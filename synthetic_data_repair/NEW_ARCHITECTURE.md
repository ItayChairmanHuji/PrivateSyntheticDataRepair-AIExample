# New Architecture: Resources, Processes, Utilities (RPM)

## The Problem: The "Quadratic Trap" and File Bloat
The previous ICM (Interpretable Context Methodology) stage-based architecture (s01-s06) was excellent for isolation but struggled with scale:
1.  **Redundancy:** Every stage required copying data from the previous stage's `output/` to the current stage's `input/`.
2.  **File Bloat:** Experiment sweeps (e.g., 1000 jobs) generated thousands of duplicate configuration files and intermediate folders.
3.  **Rigidity:** Stages were monolithic. Re-sampling a model or running a quick violation check required running the entire stage.

## The Solution: The RPM Model
The new architecture shifts from **Stages** to **Functional Components** organized by their role in the system.

### 1. Resources (`r_resources/`) - The "State"
- **Centralized State:** All data, models, and results are stored in a parameter-driven hierarchy.
- **Parameter Identity:** A resource's path is a pure function of the parameters that created it (e.g., `synth/eps/seed/size/data.csv`).
- **No Manual I/O:** Processes read/write directly to this area using the `ResourceManager` (u_io).

### 2. Processes (`p_processes/`) - The "Verbs"
- **Granular Execution:** Broad stages are decomposed into atomic processes (e.g., `p02a_training` and `p02b_sampling`).
- **Thin Wrappers:** Processes are thin CLI entry points that orchestrate shared utilities.
- **Hydra-Native:** Sweeps are handled in-memory via Hydra `--multirun`, eliminating configuration bloat.

### 3. Utilities (`u_utilities/`) - The "Tools"
- **Atomic Logic:** Shared logic (loading, synthesis, violation finding) is extracted into importable packages.
- **Library + CLI:** Every utility is both a high-quality Python library and a standalone CLI tool.
- **SRP (Single Responsibility):** Logic is never duplicated between processes.

## Key Benefits
- **Zero-Friction Sync:** Automated Git (Code) and SCP (Data) synchronization.
- **90% Less Metadata:** Consolidated registries and delta-based blueprints.
- **High Granularity:** Run exactly what you need, when you need it.
- **Physical Idempotency:** Running with the same parameters always hits the same physical path.
