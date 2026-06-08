# The RPM Gold Standard: Architectural & Refactoring Blueprint

This document codifies the "Gold Standard" for building and refactoring modules within the RPM framework. It serves as a meta-guide for future development, ensuring that every folder is clean, modular, documented, and verified.

---

## 1. The Design Philosophy

### A. Separation of Concerns (The "Triad")
Every complex utility or process should be split into three distinct layers:
1.  **The Engine (Where)**: A dedicated component for path resolution and environment logic (e.g., `PathResolver`).
2.  **The Workers (How)**: Atomic, specialized classes that perform specific tasks (e.g., `Loaders`, `Encoders`, `Solvers`).
3.  **The Facade (When)**: A high-level orchestrator that coordinates the Engine and Workers to provide a clean public API (e.g., `ResourceManager`).

### B. Dependency Injection (DI)
Inheritance should be avoided in favor of composition. Facades should receive their engines and workers as injectable dependencies. This allows for:
- **Testability**: Easy mocking of sub-components.
- **Flexibility**: Swapping logic without modifying the orchestrator.

### C. Smart Autonomy
Components should be "smart" enough to discover their own context. For example, a loader should be able to walk up a directory tree to find its metadata rather than requiring the orchestrator to pass every path manually.

---

## 2. Implementation Standards

### A. The 100/10 Rule
- **Max 100 lines per file**: If a file exceeds this, it is likely doing too much. Modularize.
- **Max 10 lines per function**: Functions should be atomic and declarative. If logic is complex, extract it into private helper methods.

### B. Declarative Dispatching
Use Python's `match case` for high-level dispatching. The "Main" resolution method should be a clean router that delegates specific implementation details to private methods.

### C. Enum-Driven Type Safety
Use Enums to define modes, categories, and stages. Avoid "stringly-typed" APIs to prevent runtime errors and improve discoverability.

### C. The "Glass Box" Documentation Standard (Rigorous Edition)
We do not believe in cluttered in-code documentation. Code should be readable "at a glance," but logic must be fully externalized.
1.  **Remove Trivial Comments**: No `# Load data` or `# Initialize class`.
2.  **Externalize Blueprints**: Every `src/` and `tests/` directory must contain an `internal_readme.md`.
3.  **The Reimplementation Test**: A senior engineer should be able to read the `internal_readme.md` and reimplement the entire module's logic from scratch without looking at the source code.
4.  **Content Mandate**: Documentation must include:
    - **Theory of Operation**: The mathematical or logical principle behind the code.
    - **Implementation Logic**: Step-by-step algorithms, state management details, and edge-case handling.
    - **Pseudo-code**: Every algorithmic implementation MUST have a clear, high-level pseudo-code block for verification and reimplementation.
    - **Contract Definition**: Detailed explanation of inputs, outputs, and side effects.

## 4. The "Mock-Hierarchy" Testing Standard

Tests must be hermetic and verify logic, not environment state.
1.  **Localized Mocking**: Use `pytest` fixtures to create a temporary, minimal version of the project's folder hierarchy.
2.  **Contract Verification**: Tests should verify the "Contract" between components—not just successful execution, but correct mapping and error handling for missing files.

---

## 5. The Refactoring Workflow (The "Surgical" Process)

When refactoring an existing folder, follow this sequence:
1.  **Research**: Map the existing logic and identify the "Monoliths."
2.  **Decompose**: Break monolithic files into atomic classes (one per file).
3.  **Engine First**: Extract path/environment logic into a standalone Resolver.
4.  **Facade Rebuild**: Reconstruct the Orchestrator using DI.
5.  **Stitch & Simplify**: Use `match-case` and private methods to collapse redundant logic.
6.  **Externalize Docs**: Move implementation details to `internal_readme.md`.
7.  **Validate**: Create a mock-hierarchy test suite to ensure the new architecture holds.

---

## 6. Lessons from the Field (Case Study: p01_loading)

During the refactoring of the `p01_loading` process, several critical patterns were identified that should be applied to all future migrations:

### A. The Serialization Mandate
The "Glass Box" principle requires intermediate artifacts to be readable (JSON/CSV).
- **Pitfall**: Passing complex objects (like `sklearn.LabelEncoder`) directly to I/O utilities.
- **Rule**: Always convert domain objects to serializable dictionaries before saving. If a shared utility (like `u_io`) is used, it must be robust enough to handle these conversions internally or enforce a serializable contract.

### B. The Resolver Bridge Pattern
Processes often act as bridges between external sources and internal resources.
- **Pattern**: Use a dedicated `Resolver` (e.g., `LoadingResolver`) in the Worker to handle the "dirty" external paths, keeping the Orchestrator focused purely on the "clean" RPM resource logic.

### C. Hydra Nesting Resilience
Hydra's default behavior can sometimes nest configurations (e.g., `cfg.loading.orchestrator` instead of `cfg.orchestrator`).
- **Best Practice**: In `main.py`, use a resilient accessor pattern: `target_cfg = cfg.orchestrator if "orchestrator" in cfg else cfg.loading.orchestrator`.

### D. Explicit Target Paths
When configuring Hydra `_target_` values, always use the full module path (e.g., `p_processes.p01_loading.src.orchestration.loading_orchestrator.LoadingOrchestrator`) and ensure all parent directories contain `__init__.py` files.

---

*This standard was last updated after the refactoring of `p01_loading` on June 5, 2026.*
