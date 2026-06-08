# Classic VC Repair (p04b)

Classic repair algorithm using edge-based random selection.

## Structure
- `main.py`: Entry point using the shared `RepairingWorker`.
- `src/core/classic_vc_repairer.py`: Bespoke implementation of the random edge selection loop.

## Algorithm
1. Build a `SymbolicConflictGraph` of all DC violations.
2. Select a random active edge (u, v) from the graph.
3. Randomly select one of the endpoints (u or v).
4. Remove the selected vertex and all its incident edges.
5. Repeat until the graph has no edges.

## Inputs
- **Synthetic Dataset**: `Dataset` object containing violating rows.
- **Marginals**: `MarginalSet` object.

## Parameters
- `alpha`: Baseline removal weight (Default: 0.5).
