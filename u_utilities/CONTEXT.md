# Utilities (u_utilities)

## Purpose
Utilities are the "Tools" of the framework. They contain the core algorithms, entities, and plumbing logic shared across processes.

## Design Principles
1. **Importability:** Every utility is a standard Python package.
2. **Atomic Logic:** Each utility has a single responsibility (e.g., `u_violation_finder`).
3. **CLI Interface:** Every utility has a `main.py` for manual testing and one-off tasks.
4. **Independence:** Utilities should minimize cross-utility dependencies to remain "Atomic."

## Core Utilities
- **`u_shared`**: Common research entities (Dataset, DC, Marginal).
- **`u_io`**: The `ResourceManager` (The Linker between Config and Path).
- **`u_loading`**: Data ingestion and encoding.
- **`u_synthesis`**: Training and sampling logic.
- **`u_remote`**: Zero-Friction synchronization with the cluster.
- **`u_violation_finder`**: DC violation detection engines.
