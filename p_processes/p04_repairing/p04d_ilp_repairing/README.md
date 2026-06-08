# ILP Repair (p04d)

Exact repair formulation using Integer Linear Programming.

## Structure
- `main.py`: Entry point using the shared `RepairingWorker`.
- `src/core/ilp_repairer.py`: Bespoke ILP formulation using Gurobi.

## Algorithm
Uses Gurobi to minimize:
`Objective = alpha * (Removal_Loss) + (1 - alpha) * (Marginal_Error)`

Constraints:
- For every violation pair (i, j): `x_i + x_j <= 1` (Standard VC constraint).

## Inputs
- **Synthetic Dataset**: `Dataset` object.
- **Marginals**: `MarginalSet` object.

## Parameters
- `alpha`: Weighting between removal loss and marginal error.
- `use_marginals`: If false, performs a simple Minimum Vertex Cover.
- `gurobi_params`: Dictionary of solver parameters (e.g., `TimeLimit`, `OutputFlag`).
