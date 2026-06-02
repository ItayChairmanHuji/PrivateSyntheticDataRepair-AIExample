# Stage 06 Execution Example: Analysis Notebooks

## 1. What you need to insert (Input)
- A directory containing raw `.json` evaluation results (e.g., `s05_evaluating/output`).
- A Python template script (`.py`) for the notebook, partitioned by `# %%` markers.

## 2. What I expect to see (Process)
The AI agent executes the helper scripts to automate the data aggregation and notebook generation:

```bash
# 1. Aggregate JSON files into a single CSV
python s06_analysis/src/io/aggregator.py \
    --source s05_evaluating/output \
    --output s06_analysis/input/flattened_results.csv

# 2. Convert the Python template into a .ipynb Notebook
python s06_analysis/src/io/notebook_generator.py \
    --template s06_analysis/src/analysis/analysis_template.py \
    --output s06_analysis/notebooks/experiment_analysis.ipynb
```

**Example Python Template Structure (`analysis_template.py`):**
```python
# %%
# [MARKDOWN]
# # Experiment Analysis

# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('../input/flattened_results.csv')

# %%
# [MARKDOWN]
# ## TVD by Dataset

# %%
g = sns.FacetGrid(df, col="dataset", sharey=False)
g.map_dataframe(sns.scatterplot, x="epsilon", y="tvd_repaired", hue="repair_algorithm", style="synthesizer")
g.add_legend()
plt.show()
```

## 3. What I will output (Output)
- `s06_analysis/input/flattened_results.csv`: The aggregated metrics dataset.
- `s06_analysis/notebooks/experiment_analysis.ipynb`: A well-formatted Jupyter Notebook combining markdown explanations and plotting code, strictly separated by dataset, colored by algorithm, and styled by synthesizer.
