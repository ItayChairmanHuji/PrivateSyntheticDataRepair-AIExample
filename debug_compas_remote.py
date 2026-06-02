import pandas as pd
import json
from pathlib import Path

exp_path = "final_research/outputs/experiment_7_repair_comparison/exp_481"
syn_data_path = f"{exp_path}/s02_synthesizing/compas/synthetic_data.csv"
marginals_path = f"{exp_path}/s03_marginals/compas/marginals.json"

print(f"--- Checking COMPAS Synthetic Data (exp_481) ---")
try:
    df = pd.read_csv(syn_data_path)
    print(f"Synthetic Data Shape: {df.shape}")
    print("\nColumns and unique values (first few):")
    for col in df.columns[:5]:
        print(f"  {col}: {df[col].unique()[:5]}")
except Exception as e:
    print(f"Error reading synthetic data: {e}")

print(f"\n--- Checking Marginals vs Synthetic ---")
try:
    with open(marginals_path, 'r') as f:
        m_data = json.load(f)
    
    marginals = m_data['marginals'][:5]  # Check first 5
    for i, m in enumerate(marginals):
        attrs = m['attrs']
        values = m['values']
        target = m['target']
        
        # Calculate freq in syn
        mask = pd.Series(True, index=df.index)
        for attr, val in zip(attrs, values):
            mask &= (df[attr].astype(str) == str(val))
        
        syn_count = mask.sum()
        syn_freq = syn_count / len(df)
        rel_error = abs(syn_freq - target) / (target + 1e-10)
        
        print(f"Marginal {i+1}: {attrs} = {values}")
        print(f"  Target Freq: {target:.4f}")
        print(f"  Syn Freq:    {syn_freq:.4f} (Count: {syn_count})")
        print(f"  Rel Error:   {rel_error:.4f}")

except Exception as e:
    print(f"Error checking marginals: {e}")
