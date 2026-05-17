import os
import json
import pandas as pd
import numpy as np

results_dir = 'results_alpha_eps01/results'
data_list = []

for root, dirs, files in os.walk(results_dir):
    for file in files:
        if file.endswith('.json'):
            with open(os.path.join(root, file), 'r') as f:
                try:
                    d = json.load(f)
                    name = d.get('experiment_name', '')
                    if 'weighted' in name and 'v4' in name:
                        meta = d.get('metadata', {})
                        acc_dict = d.get('ml_accuracy', {}).get('repaired', {})
                        acc = np.mean(list(acc_dict.values())) if acc_dict else None
                        
                        data_list.append({
                            'dataset': d.get('dataset_name'),
                            'alpha': meta.get('repairer_params', {}).get('alpha'),
                            'seed': meta.get('synthesizer_params', {}).get('seed'),
                            'ml_accuracy': acc,
                            'marginal_error': d.get('marginals_error', {}).get('repaired_avg')
                        })
                except:
                    pass

df = pd.DataFrame(data_list)
print(f"Total rows: {len(df)}")
if not df.empty:
    stats = df.groupby(['dataset', 'alpha'])['ml_accuracy'].agg(['mean', 'std', 'count']).reset_index()
    stats = stats[stats['count'] > 1]
    print("\nVariance in ML Accuracy (Top 10):")
    for _, row in stats.sort_values('std', ascending=False).head(10).iterrows():
        print(f"Dataset: {row['dataset']:10} Alpha: {row['alpha']:<5} Std: {row['std']:.4f} Mean: {row['mean']:.4f} Count: {int(row['count'])}")

    stats_err = df.groupby(['dataset', 'alpha'])['marginal_error'].agg(['mean', 'std', 'count']).reset_index()
    stats_err = stats_err[stats_err['count'] > 1]
    print("\nVariance in Marginal Error (Top 10):")
    for _, row in stats_err.sort_values('std', ascending=False).head(10).iterrows():
        print(f"Dataset: {row['dataset']:10} Alpha: {row['alpha']:<5} Std: {row['std']:.4f} Mean: {row['mean']:.4f} Count: {int(row['count'])}")
