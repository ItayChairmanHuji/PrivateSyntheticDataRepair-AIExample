# Stage 08 Execution Example: Analysis Notebooks

## 1. What you need to insert (Input)
- `aggregated_results.csv` from Stage 07.

## 2. What I expect to see (Process)
You open a notebook in `08_analysis/notebooks/` and load the CSV.

**Example Logic:**
```python
import pandas as pd
import seaborn as sns

df = pd.read_csv('../07_result_syncing/output/aggregated_results.csv')
sns.lineplot(data=df, x='alpha', y='tvd')
```

## 3. What I will output (Output)
- Plots and insights documented in the notebook.
- `output/final_summary_plot.png`.
