# Marginals Obtaining 

## Goal
The marginals obtaining stage is responsible for identifying and extracting the most relevant statistical properties (marginals) from the private dataset to guide the repair of the synthetic dataset.

## Marginals Obtainers 
1. **Obtainer**: Abstract base class for all marginal extraction strategies. 
2. **Top K**: A differentially private selection mechanism. It uses the Exponential Mechanism (via the Gumbel trick) to select the `k` marginals with the highest utility scores. 
   - **Selection**: Guided by a `UtilityFunction` and a `selection_budget`.
   - **Generation**: After selection, Gaussian noise is added to the private frequencies of the selected marginals based on the `generation_budget`.

### Utility Functions
1. **Distance**: Calculates utility based on the absolute difference between the private and synthetic marginal frequencies. Higher distance means higher utility (the repair needs more information there).

## Testing
The marginals obtaining system is verified by tests in `tests/marginals_obtaining/`.

### 1. Top K Obtainer Tests (`test_top_k_obtainer.py`)
Validates the core logic of the `TopKObtainer` and its integration with utility functions:
- **Frequency Computation**: Verifies that `_compute_all_2way_marginals` correctly calculates 2-way joint distributions from raw DataFrames.
- **Selection Logic**: Ensures that the obtainer respects the `k` parameter and returns the requested number of marginals.
- **Privacy Mechanism**: Checks that the returned marginal targets are within the valid frequency range [0, 1] after noise addition.
- **Robustness**: Tests handling of edge cases such as empty datasets or extremely low privacy budgets.

