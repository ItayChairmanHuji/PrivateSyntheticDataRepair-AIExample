# Utility: u_violation_finder

## Purpose
High-performance detection of Denial Constraint (DC) violations.

## Interface
- **`ViolationFinder`**: Orchestrates engines to find all violations in a dataset.
- **`ValueGroupedEngine`**: Vectorized violation finder for categorical data.
- **`SqlEngine`**: DuckDB-powered finder for inequality/range constraints.

## Usage
```python
from u_utilities.u_violation_finder import ViolationFinder
finder = ViolationFinder()
violations = finder.find_violations(data, dcs)
```
