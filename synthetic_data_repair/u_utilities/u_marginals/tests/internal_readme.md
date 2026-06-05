# Tests: u_marginals

## Purpose
Verifies the modular RPM architecture for marginal distribution management.

## Test Coverage
- **`test_marginal_calculator`**: Ensures frequency computation and alignment are correct.
- **`test_marginal_error`**: Verifies distance metrics (ABS).
- **`test_marginal_manager_obtain`**: Validates the full orchestration flow for Top-K selection, including noisy generation and encoding.
- **`test_marginal_manager_invalid_method`**: Ensures proper error handling for unsupported selection methods.

## Mock Strategy
Uses `pytest` fixtures to create in-memory `Dataset` objects with small DataFrames, avoiding disk I/O for logic verification.
