# Utility: u_visualizer

## Purpose
Standardized plotting library for research results.

## Interface
- **`ResultPlotter`**: Splits plots by dataset and repair algorithm.
- **`GraphVisualizer`**: Visualizes violation graphs and biclique distributions.

## Usage
```python
from u_utilities.u_visualizer import ResultPlotter
plotter = ResultPlotter()
plotter.plot_utility_vs_epsilon(results_df)
```
