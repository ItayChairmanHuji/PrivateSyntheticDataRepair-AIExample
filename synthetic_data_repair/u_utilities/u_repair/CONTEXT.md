# Repair Utility (`u_repair`)

## Purpose
This utility provides highly optimized algorithms for repairing synthetic datasets that violate Denial Constraints (DCs). It focuses on the **Weighted Vertex Cover (VC)** approach, which balances data preservation (Utility) with violation removal (Greedy).

## Core Components

### 1. Repairers (`src/`)
- **`WeightedVCRepairer`**: The primary repairer. Uses a greedy selection formula:
  `Score = (1 - alpha) * Utility + alpha * Degree`
- **`VertexCoverRepairer`**: Abstract base class for all VC-based repairers.
- **`Repairer`**: Top-level interface for all repair strategies.

### 2. Graph Representations (`src/symbolic_graph.py`)
To avoid $O(N^2)$ memory bottlenecks, we use:
- **`SymbolicConflictGraph`**: A virtual graph that performs degree calculation and vertex deletion using compressed **Bicliques**.
- **`GroupAwareGraph`**: An optimization for categorical data that treats identical rows as a single vertex, speeding up repair by orders of magnitude.

### 3. Adaptive Alpha (`src/adaptive_alpha_calculator.py`)
- Automatically calculates the optimal balance between utility and greedy repair based on the graph's hubbiness and connectivity.

## Usage
```python
from u_utilities.u_repair import WeightedVCRepairer
from u_utilities.u_shared import Dataset, MarginalSet

repairer = WeightedVCRepairer(alpha=0.5)
repaired_dataset = repairer.repair(synthetic_dataset, marginals)
```

## Optimizations
- **Vectorized Utility**: Uses matrix multiplication to calculate the impact of row removal on all marginals simultaneously.
- **Zero Materialization**: Never creates a physical edge list for conflicts.
- **Biclique Compression**: Stores $1000 \times 1000$ conflicts in 2KB instead of 4MB.
