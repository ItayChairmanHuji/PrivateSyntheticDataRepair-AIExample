# Shared Repair Infrastructure

Shared plumbing for the `p04_repairing` group.

## Components
- `repairer.py`: The `Repairer` abstract base class defining the `repair(dataset, marginals)` interface.
- `symbolic_graph.py`: A high-performance conflict graph implementation. It uses a "Symbolic" representation of bicliques to avoid materializing the full adjacency matrix of large violation sets.
