# Weighted VC Repair (p04c)

Highly optimized repair algorithm that balances row removal with marginal utility. It utilizes a **Dependency Injection (DI)** architecture to decouple the selection orchestrator from the weighting and balancing strategies.

## Structure
- `main.py`: Entry point using the shared `RepairingWorker`.
- `src/core/weighted_vc_repairer.py`: Clean orchestrator loop that manages graph interactions and vertex selection.
- `src/core/weights/`: Sub-package for `WeightCalculator` abstractions and implementations (e.g., `MarginalWeightCalculator`).
- `src/core/alpha/`: Sub-package for `AlphaCalculator` abstractions and implementations (e.g., `AdaptiveAlphaCalculator`, `ConstantAlphaCalculator`).

## Algorithm
1. Build a `SymbolicConflictGraph` via `ConflictGraphBuilder`.
2. Initialize `WeightCalculator` (e.g., `MarginalWeightCalculator`) and `AlphaCalculator`.
3. Loop while the graph has edges:
    a. Get weights from the `WeightCalculator`.
    b. Get degrees from the `Graph`.
    c. Get alpha from the `AlphaCalculator`.
    d. Select a vertex minimizing the weighted ratio: `(1 - alpha) * weights - alpha * degrees`.
    e. Remove vertex from graph and update `WeightCalculator` state.

## Inputs
- **Synthetic Dataset**: `Dataset` object.
- **Marginals**: `MarginalSet` object representing target statistics.

## Parameters
- `alpha`: Base alpha value if not using adaptive modes.
- `use_adaptive_alpha`: Use `AdaptiveAlphaCalculator` to dynamically balance utility vs removal.
- `use_auto_alpha`: Use Coefficient of Variation (CV) based alpha.
