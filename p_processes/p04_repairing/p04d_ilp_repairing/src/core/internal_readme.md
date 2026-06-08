# ILP Repairing (Internal)

This sub-process implements the repairing task as an Integer Linear Program (ILP) solved via Gurobi.

## Components

- **Repairer**: `ILPRepairer` (located in `src/core/ilp_repairer.py`).
- **Solver**: Gurobi Optimizer.

## Characteristics

- **Optimality**: Guarantees the optimal solution (minimal removals for a given utility constraint) within the problem formulation.
- **Complexity**: May be slower than greedy approaches for very large datasets.
