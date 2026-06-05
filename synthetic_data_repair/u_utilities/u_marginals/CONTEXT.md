# Utility: u_marginals

## Purpose
Logic for defining, calculating, selecting, and comparing N-way marginal distributions with Differential Privacy.

## Interface
- **`MarginalManager`**: The Facade for obtaining marginals from datasets.
- **`MarginalCalculator`**: Computes counts/frequencies for specified attribute sets.
- **`MarginalError`**: Measures distance (ABS/RMSE) between two marginal sets.

## Usage
```python
from u_utilities.u_marginals import MarginalManager
manager = MarginalManager()
m_set = manager.obtain(p_dataset, s_dataset, k=20, selection_budget=0.5)
```
