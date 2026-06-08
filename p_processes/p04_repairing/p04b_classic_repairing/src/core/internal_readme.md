# Classic Repairing (Internal)

This sub-process implements the "Classic" Vertex Cover repair strategy. It uses a random selection approach to resolve conflicts.

## Components

- **Repairer**: `ClassicVCRepairer` (located in `src/core/classic_vc_repairer.py`).
- **Graph**: Uses `GroupAwareGraph` if group information is available, otherwise falls back to `SymbolicConflictGraph`.

## Characteristics

- **Randomized Selection**: Picks a random node from the conflict graph to remove.
- **Baseline**: Serves as a baseline for more advanced repair strategies.
