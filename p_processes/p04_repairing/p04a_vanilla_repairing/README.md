# Vanilla VC Repair (p04a)

Baseline repair algorithm using a Max-Degree Vertex Cover heuristic.

## Structure
- `main.py`: Entry point using the shared `RepairingWorker`.
- `src/core/vanilla_vc_repairer.py`: Bespoke implementation of the Max-Degree selection loop.

## Algorithm
1. Build a `SymbolicConflictGraph` of all DC violations.
2. Iteratively select the vertex with the highest degree (most violations).
3. Remove selected vertex and all its incident edges.
4. Repeat until the graph has no edges (`has_edges()` is False).

## Inputs
- **Synthetic Dataset**: `Dataset` object containing violating rows.
- **Marginals**: `MarginalSet` object.

## Parameters
- `alpha`: Baseline removal weight (Default: 0.5).
