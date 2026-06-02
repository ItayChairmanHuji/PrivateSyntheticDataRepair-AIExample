# %%
# [MARKDOWN]
# # Experiment 8 Analysis: Large Scale VC Repair (300K)
# Comparison of Vanilla, Classic, and Weighted VC (with Dynamic Alpha) as a function of Epsilon on 300,000 rows.

# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Configure seaborn styling
sns.set_theme(style="whitegrid")

# Load flattened data
DATA_PATH = Path("../input/experiment_8_repair_comparison_flat.csv")
df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df)} records.")
df.head()

# %%
# [MARKDOWN]
# ## 1. Deletion Ratio by Dataset
# Analyzes the deletion ratio trends using line plots for each dataset.

# %%
datasets = sorted(df['dataset'].unique())

for dataset in datasets:
    plt.figure(figsize=(12, 6))
    subset = df[df['dataset'] == dataset]
    
    sns.lineplot(
        data=subset, 
        x="epsilon", 
        y="deletion_ratio", 
        hue="repair_algorithm", 
        style="synthesizer", 
        markers=True, 
        dashes=True,
        err_style="band",
        alpha=0.8
    )
    
    plt.title(f"Deletion Ratio vs Epsilon - Dataset: {dataset.upper()} (300K)")
    plt.ylabel("Deletion Ratio")
    plt.xlabel("Epsilon (Privacy Budget)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

# %%
# [MARKDOWN]
# ## 2. Marginals Error
# Comparative analysis of average 1-way marginals error after repair.

# %%
for dataset in datasets:
    plt.figure(figsize=(12, 6))
    subset = df[df['dataset'] == dataset]
    
    sns.lineplot(
        data=subset, 
        x="epsilon", 
        y="marginals_error_repaired", 
        hue="repair_algorithm", 
        style="synthesizer", 
        markers=True, 
        dashes=True,
        err_style="band"
    )
    
    plt.title(f"Marginals Error vs Epsilon - Dataset: {dataset.upper()}")
    plt.ylabel("Marginals Error (Repaired)")
    plt.xlabel("Epsilon")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

# %%
# [MARKDOWN]
# ## 3. Total Variation Distance (TVD)
# 2-way marginals distribution similarity.

# %%
for dataset in datasets:
    plt.figure(figsize=(12, 6))
    subset = df[df['dataset'] == dataset]
    
    sns.lineplot(
        data=subset, 
        x="epsilon", 
        y="tvd_repaired", 
        hue="repair_algorithm", 
        style="synthesizer", 
        markers=True, 
        dashes=True
    )
    
    plt.title(f"TVD vs Epsilon - Dataset: {dataset.upper()}")
    plt.ylabel("TVD (Repaired)")
    plt.xlabel("Epsilon")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

# %%
# [MARKDOWN]
# ## 4. Alpha Parameter Evolution (Weighted VC)
# Analysis of the dynamic alpha reselection for Weighted VC.

# %%
plt.figure(figsize=(12, 6))
weighted_df = df[df['repair_algorithm'] == 'weighted_vc']

if not weighted_df.empty:
    sns.lineplot(
        data=weighted_df,
        x="epsilon",
        y="mean_alpha",
        hue="dataset",
        style="synthesizer",
        markers=True
    )

    plt.title("Dynamic Alpha Mean vs Epsilon (Weighted VC)")
    plt.ylabel("Mean Alpha (1-Connectivity)")
    plt.xlabel("Epsilon")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
else:
    print("No weighted_vc results available yet.")

# %%
# [MARKDOWN]
# ## 5. Runtime Comparison
# Comparing the efficiency of the three algorithms at 300K scale.

# %%
for dataset in datasets:
    plt.figure(figsize=(12, 6))
    subset = df[df['dataset'] == dataset]
    
    sns.lineplot(
        data=subset, 
        x="epsilon", 
        y="repair_runtime", 
        hue="repair_algorithm", 
        style="synthesizer", 
        markers=True, 
        dashes=True
    )
    
    plt.title(f"Runtime vs Epsilon - Dataset: {dataset.upper()}")
    plt.ylabel("Runtime (seconds)")
    plt.xlabel("Epsilon")
    plt.yscale('log')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
