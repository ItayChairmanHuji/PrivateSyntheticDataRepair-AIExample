# Vanilla Repairing (Internal)

This sub-process implements the "Vanilla" Vertex Cover repair strategy. It uses a greedy approach based on node degrees to resolve conflicts.

## Components

- **Repairer**: `VanillaVCRepairer` (located in `src/core/vanilla_vc_repairer.py`).
- **Graph**: Uses `GroupAwareGraph` if group information is available in the violations, otherwise falls back to `SymbolicConflictGraph`.

## Characteristics

- **Greedy Selection**: Always picks the node with the highest degree to remove.
- **Performance**: Very fast due to the use of symbolic graph representations.
