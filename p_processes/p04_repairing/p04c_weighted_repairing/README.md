# Weighted VC Repair (p04c)

Highly optimized repair algorithm that balances row removal with marginal utility.

## Structure
- `main.py`: Entry point using the shared `RepairingWorker`.
- `src/core/weighted_vc_repairer.py`: Bespoke implementation of the weight-balanced selection loop.
- `src/core/adaptive_alpha_calculator.py`: Logic for dynamic alpha adjustment.

## Algorithm
1. Build a `SymbolicConflictGraph` or `GroupAwareGraph`.
2. For each iteration:
    a. Calculate a "Marginal Weight" for each row based on its contribution to statistical error.
    b. Calculate an "Alpha" parameter (Adaptive or Auto) based on graph topology.
    c. Select a vertex minimizing: `(1 - alpha) * weight - alpha * degree`.
    d. Remove vertex and update marginal error counts.

## Inputs
- **Synthetic Dataset**: `Dataset` object.
- **Marginals**: `MarginalSet` object representing target statistics.

## Parameters
- `alpha`: Base alpha value if not using adaptive modes.
- `use_adaptive_alpha`: Use `AdaptiveAlphaCalculator` to dynamically balance utility vs removal.
- `use_auto_alpha`: Use Coefficient of Variation (CV) based alpha.
