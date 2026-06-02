# %%
# [MARKDOWN]
# # Experiment 5 Analysis: Repair Comparison
# Comparison of VC repair algorithms across multiple datasets and epsilons.

# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Configure seaborn styling
sns.set_theme(style="whitegrid")

# Load flattened data
DATA_PATH = Path("../input/experiment_5_results.csv")
df = pd.read_csv(DATA_PATH)

# Clean up epsilon and other numeric types if needed
df['epsilon'] = pd.to_numeric(df['epsilon'], errors='coerce')

print(f"Loaded {len(df)} records.")
df.head()

# %%
# [MARKDOWN]
# ## 1. Deletion Ratio by Dataset
# Analyzes the deletion ratio using repair algorithm as hue and synthesizer as style.

# %%
g = sns.FacetGrid(df, col="dataset", sharey=False, height=5, aspect=1.2)
g.map_dataframe(sns.scatterplot, x="epsilon", y="deletion_ratio", hue="repair_algorithm", style="synthesizer", s=100)
g.add_legend()
g.set_axis_labels("Epsilon (Privacy Budget)", "Deletion Ratio")
g.fig.suptitle("Deletion Ratio vs Epsilon", y=1.05)
plt.show()

# %%
# [MARKDOWN]
# ## 2. Marginals Error

# %%
g = sns.FacetGrid(df, col="dataset", sharey=False, height=5, aspect=1.2)
g.map_dataframe(sns.scatterplot, x="epsilon", y="marginals_error_repaired", hue="repair_algorithm", style="synthesizer", s=100)
g.add_legend()
g.set_axis_labels("Epsilon", "Marginals Error")
g.fig.suptitle("Marginals Error vs Epsilon", y=1.05)
plt.show()

# %%
# [MARKDOWN]
# ## 3. Marginals Loss

# %%
g = sns.FacetGrid(df, col="dataset", sharey=False, height=5, aspect=1.2)
g.map_dataframe(sns.scatterplot, x="epsilon", y="loss_marginal_repaired", hue="repair_algorithm", style="synthesizer", s=100)
g.add_legend()
g.set_axis_labels("Epsilon", "Marginals Loss")
g.fig.suptitle("Marginals Loss vs Epsilon", y=1.05)
plt.show()

# %%
# [MARKDOWN]
# ## 4. Total Variation Distance (TVD)

# %%
g = sns.FacetGrid(df, col="dataset", sharey=False, height=5, aspect=1.2)
g.map_dataframe(sns.scatterplot, x="epsilon", y="tvd_repaired", hue="repair_algorithm", style="synthesizer", s=100)
g.add_legend()
g.set_axis_labels("Epsilon", "Total Variation Distance (TVD)")
g.fig.suptitle("TVD vs Epsilon", y=1.05)
plt.show()

# %%
# [MARKDOWN]
# ## 5. Machine Learning Accuracy

# %%
g = sns.FacetGrid(df, col="dataset", sharey=False, height=5, aspect=1.2)
g.map_dataframe(sns.scatterplot, x="epsilon", y="ml_acc_repaired", hue="repair_algorithm", style="synthesizer", s=100)
g.add_legend()
g.set_axis_labels("Epsilon", "ML Accuracy")
g.fig.suptitle("ML Accuracy vs Epsilon", y=1.05)
plt.show()

# %%
# [MARKDOWN]
# ## 6. Runtime

# %%
g = sns.FacetGrid(df, col="dataset", sharey=False, height=5, aspect=1.2)
g.map_dataframe(sns.scatterplot, x="epsilon", y="repair_runtime", hue="repair_algorithm", style="synthesizer", s=100)
g.add_legend()
g.set_axis_labels("Epsilon", "Runtime (seconds)")
g.fig.suptitle("Runtime vs Epsilon", y=1.05)
plt.show()
