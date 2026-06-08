# Weighted Repairing (Internal)

This sub-process implements the "Weighted" Vertex Cover repair strategy. It incorporates statistical utility (marginals) into the greedy selection process.

## Components

- **Repairer**: `WeightedVCRepairer` (located in `src/core/weighted_vc_repairer.py`).
- **Utility Calculator**: `AdaptiveAlphaCalculator` (located in `src/core/adaptive_alpha_calculator.py`).
- **Graph**: Uses `GroupAwareGraph` or `SymbolicConflictGraph`.

## Characteristics

- **Utility-Aware**: Balances the removal of conflicting rows with the preservation of statistical marginals.
- **Adaptive Alpha**: Can dynamically adjust the balance between conflict resolution and utility preservation.
