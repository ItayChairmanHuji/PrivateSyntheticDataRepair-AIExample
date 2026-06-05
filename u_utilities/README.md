# Utilities (`u_utilities`)

This directory contains the shared logic, algorithms, and plumbing that power the framework. Think of these as the "Tools".

## Design
- **Shared Logic:** If code is used by more than one process, it belongs here.
- **Library & CLI:** Each utility is designed to be an importable Python library, but also includes a `main.py` for standalone CLI execution and testing.
- **Single Responsibility:** Utilities are focused and atomic (e.g., `u_io` handles paths, `u_violation_finder` finds violations).

## Core Utilities
- `u_io`: The Resource Manager (Path resolution).
- `u_loading`: Data loading and encoding logic.
- `u_synthesis`: Model training and sampling logic.
- `u_remote`: Cluster synchronization tools.

For more details on rules and AI interaction, see [CONTEXT.md](CONTEXT.md).
