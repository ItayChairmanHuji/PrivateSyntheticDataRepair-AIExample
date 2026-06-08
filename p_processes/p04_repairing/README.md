# p04_repairing: Synthetic Data Repair Orchestration

This process group manages the repair of synthetic datasets to satisfy Denial Constraints (DCs) while maintaining statistical fidelity (Marginals).

## Directory Structure

- `src/`: Shared orchestration logic.
    - `engine.py`: Handles I/O and domain object hydration (`Dataset`, `MarginalSet`).
    - `worker.py`: The unified orchestrator for the repair flow.
    - `core/`: Shared infrastructure (Base `Repairer` and `SymbolicGraph`).
- `config/`: Centralized Hydra configuration for each repair algorithm.
- `p04a_vanilla_repairing/`: Baseline Max-Degree Vertex Cover repair.
- `p04b_classic_repairing/`: Random-selection Vertex Cover repair.
- `p04c_weighted_repairing/`: Optimized Weighted VC repair with adaptive alpha support.
- `p04d_ilp_repairing/`: Exact ILP-based repair using Gurobi.

## Architecture: Shared Orchestration, Symbolic Optimization

The repair processes follow a standardized flow orchestrated by a shared **RepairingWorker**, leveraging a **Biclique-Compressed Symbolic Graph** for extreme performance at scale.

1. **Hydrate**: The `RepairingEngine` loads synthetic data and marginals into domain objects.
2. **Graph Build**: The `ConflictGraphBuilder` constructs a symbolic graph, compressing millions of edges into a few hundred blocks.
3. **Repair**: The worker invokes a bespoke `Repairer` implementation (e.g., `WeightedVCRepairer` with its modular DI weight/alpha components).
4. **Persist**: The `RepairingEngine` saves the repaired results.

### Orchestration Flow
```python
def run(self):
    synthetic_dataset = self.engine.load_synthetic_dataset(...)
    marginals = self.engine.load_marginal_set(...)
    repaired_dataset = self.repairer.repair(synthetic_dataset, marginals)
    self.engine.save_repaired_dataset(repaired_dataset, ...)
```
