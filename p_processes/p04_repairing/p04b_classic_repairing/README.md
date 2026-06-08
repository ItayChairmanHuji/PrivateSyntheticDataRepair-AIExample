# Classic VC Repair (p04b)

Classic repair algorithm using random vertex selection.

## Structure
- `main.py`: Entry point using the shared `RepairingWorker`.
- `src/core/classic_vc_repairer.py`: Bespoke implementation of the random selection loop.

## Algorithm
1. Build a `SymbolicConflictGraph` of all DC violations.
2. Randomly select an active vertex from the graph.
3. Remove selected vertex and all its incident edges.
4. Repeat until the graph is empty.

## Inputs
- **Synthetic Dataset**: `Dataset` object containing violating rows.
- **Marginals**: `MarginalSet` object.

## Parameters
- `alpha`: Baseline removal weight (Default: 0.5).
