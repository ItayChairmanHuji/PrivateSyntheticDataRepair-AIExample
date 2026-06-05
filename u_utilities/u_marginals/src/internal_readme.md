# Internal: u_marginals

## Architectural Blueprint
This utility follows the RPM Triad (Engine, Workers, Facade) for managing marginal distributions.

### 1. The Engine (`engine/`)
- **`MarginalResolver`**: Handles environment-level logic, such as resolving random seeds and selection methods.

### 2. The Workers (`workers/`)
- **`MarginalCalculator`**: Core logic for computing frequencies and aligning distributions between datasets.
- **`MarginalError`**: Implements distance metrics (ABS, RMSE) and sensitivity calculations for DP.
- **`TopKSelector`**: Implements the selection logic for identifying high-error marginals using the exponential mechanism.
- **`MarginalGenerator`**: Adds noise to marginal targets to ensure differential privacy.
- **`MarginalEncoder`**: Maps raw categorical values to encoded integers based on dataset metadata.

### 3. The Facade (`facade/`)
- **`MarginalManager`**: The primary entry point. Orchestrates the engine and workers to "obtain" marginals from data or files.

## Refactoring Notes (June 5, 2026)
- Migrated from legacy `s03_marginals` imports to local RPM workers.
- Adhered to 100/10 rule and SRP.
- Replaced `UtilityFunction` and `Obtainer` with a more modular `MarginalManager` approach.
