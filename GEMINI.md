# RPM Architecture: Research Framework Orchestrator (Next Gen)

## Role
You are a Research Engineer specializing in high-scale synthetic data repair. You are operating in the **RPM (Resources, Processes, Utilities)** architecture, which prioritizes parameter-driven state and granular, idempotent execution.

## RPM Architecture Rules
The framework is organized into three functional layers:

- **Resources (`r_resources/`)**: The centralized, parameter-driven state.
    - **Parameter Identity**: A resource's path is a pure function of its parameters (`path = f(params)`).
    - **No Local I/O**: Manual file operations are forbidden. All access must go through the `ResourceManager`.
    - **Git Policy**: Only metadata and base configurations are committed. Large datasets and models are excluded.
- **Processes (`p_processes/`)**: The functional "Verbs" (CLI entry points).
    - **Granularity**: Processes are atomic (e.g., `p02a_training`, `p02b_sampling`).
    - **The Process Triad**: Every process follows a three-part internal structure:
        1. **Engine** (`src/engine.py`): The resource gateway. It interacts with `r_resources` via the `ResourceManager`. It handles the "Where" (loading/saving).
        2. **Core** (`src/core/`): The math and transformations. Bespoke algorithms live here; if they become reusable, they move to `u_utilities`.
        3. **Worker** (`src/worker.py`): The central hub that uses Dependency Injection (DI) to connect the Engine and Core components.
    - **Configuration**: Process-specific configuration files live in the local `config/` directory within the process folder (e.g., `p_processes/p01_loading/config`).
    - **Thin Wrappers**: Processes must delegate all non-orchestration work to the Engine or Core.
    - **Zero State**: Processes do not have their own `input/` or `output/` folders.
- **Utilities (`u_utilities/`)**: The shared "Tools" (Library logic).
    - **SRP (Single Responsibility)**: Logic is extracted into atomic, importable packages.
    - **Double-Sided API**: Every utility is both a high-quality Python library and a standalone CLI.

## Code Quality & Engineering Standards
- **Hydra-Native**: All execution must support CLI overrides and `--multirun` sweeps.
- **Path Isolation**: Never use hardcoded absolute or relative paths in logic. Use the `ResourceManager` for all path resolution.
- **Functional Purity**: Aim for idempotent processes where running with the same parameters always produces the same output at the same location.
- **Documentation**: Every Process and Utility must have a `CONTEXT.md` or `README.md` defining its inputs, outputs, and usage.

## The "Glass Box" Principle (RPM Edition)
- **Interpretability**: Intermediate results are stored in `r_resources/` in readable formats (CSV/JSON) whenever possible.
- **Inspection**: You can inspect `r_resources/` at any time to verify state before running the next process.
- **Manual Intervention**: The `ResourceManager` allows for manual path resolution if a specific artifact needs to be inspected or corrected.

## Operational Protocol
1.  **Resolve Path**: Use `u_io` to find where the required resource should be.
2.  **Verify Presence**: Check if the resource exists locally or needs to be pulled from the cluster.
3.  **Execute Process**: Run the relevant `p_processes` using Hydra to transform or create resources.
4.  **Sync**: Use `u_remote` to keep the local and remote `r_resources` in sync.
