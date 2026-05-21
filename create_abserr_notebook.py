import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Alpha Sweep (Absolute Error) Experiment Analysis\n",
    "Analysis of how the `alpha` hyperparameter affects metrics when using Absolute Error weights. \n",
    "Experiment: `alpha_eps01_b1000_abserr`"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "import os\n",
    "\n",
    "# Set visual style\n",
    "sns.set_theme(style=\"whitegrid\")\n",
    "plt.rcParams['figure.figsize'] = [12, 6]\n",
    "\n",
    "# Load aggregated data\n",
    "csv_path = '../experiments_alpha_eps01_b1000_abserr.csv'\n",
    "if not os.path.exists(csv_path):\n",
    "    csv_path = '../experiment_results_summary.csv' # Fallback\n",
    "    \n",
    "df = pd.read_csv(csv_path)\n",
    "\n",
    "# Filter for this specific experiment\n",
    "df = df[df['experiment_name'].str.contains('alpha_eps01_b1000_abserr', na=False)].copy()\n",
    "\n",
    "# Map new flattened column names to expected shorter names\n",
    "rename_map = {\n",
    "    'meta_repairer_params_alpha': 'alpha',\n",
    "    'meta_obtainer_params_k': 'k',\n",
    "    'meta_obtainer_params_selection_budget': 'sel_budget',\n",
    "    'meta_obtainer_params_generation_budget': 'gen_budget',\n",
    "    'meta_synthesizer_params_seed': 'seed',\n",
    "    'meta_synthesizer_params_size': 'iters'\n",
    "}\n",
    "df = df.rename(columns=rename_map)\n",
    "\n",
    "# Clean up names\n",
    "df['repairer'] = df['repairer'].str.replace('Repairer', '').str.replace('VC', '-VC')\n",
    "df['engine'] = df['engine'].fillna('Unknown')\n",
    "\n",
    "print(f\"Total Alpha Sweep records: {len(df)}\")\n",
    "print(\"Records by Dataset:\", df.groupby('dataset').size().to_dict())\n",
    "print(\"Records by Engine:\", df.groupby('engine').size().to_dict())\n",
    "print(\"Alphas present:\", sorted(df['alpha'].unique()))\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Visualizing Metrics vs. Alpha"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "metrics = {\n",
    "    'deletion_ratio_ratio': 'Deletion Ratio',\n",
    "    'tvd_2way_repaired_avg': 'Total Variation Distance (TVD)',\n",
    "    'marginals_error_repaired_avg': 'Marginal Error',\n",
    "    'runtime_repairing': 'Repair Runtime (seconds)',\n",
    "    'loss_function_repaired_total': 'Total Loss Function Value',\n",
    "    'ml_accuracy_repaired_logistic_regression': 'ML Accuracy (Logistic Regression)'\n",
    "}\n",
    "\n",
    "def plot_metric_vs_alpha(dataset_name, metric_col, metric_title):\n",
    "    ds_df = df[(df['dataset'] == dataset_name) & (df['alpha'].notna())].copy()\n",
    "    if ds_df.empty:\n",
    "        return\n",
    "    \n",
    "    plt.figure(figsize=(12, 6))\n",
    "    # Note: Using engine as hue since we are mostly comparing AIM vs MST in this sweep\n",
    "    sns.lineplot(data=ds_df, x='alpha', y=metric_col, hue='engine', markers=True, dashes=False)\n",
    "    plt.title(f\"{metric_title} vs. Alpha (AbsErr)\\n{dataset_name.upper()} Dataset\", fontsize=14)\n",
    "    plt.xlabel(\"Alpha Value\", fontsize=12)\n",
    "    plt.ylabel(metric_title, fontsize=12)\n",
    "    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')\n",
    "    plt.tight_layout()\n",
    "    plt.show()\n",
    "\n",
    "datasets = df['dataset'].dropna().unique()\n",
    "for ds in datasets:\n",
    "    print(f\"\\n{'='*50}\")\n",
    "    print(f\"Dataset: {ds.upper()}\")\n",
    "    print(f\"{'='*50}\\n\")\n",
    "    for m_col, m_title in metrics.items():\n",
    "        if m_col in df.columns:\n",
    "            try:\n",
    "                plot_metric_vs_alpha(ds, m_col, m_title)\n"
    "            except Exception as e:\n",
    "                print(f\"Error plotting {m_title}: {e}\")\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('notebooks/alpha_eps01_b1000_abserr_analysis_v2.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)
