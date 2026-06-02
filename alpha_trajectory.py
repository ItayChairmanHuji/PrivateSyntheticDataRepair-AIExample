import pandas as pd
import ast
import json

def analyze_alpha_trajectory():
    df = pd.read_csv('remote/output/experiment_7_repair_comparison_summary.csv', low_memory=False)
    
    # Filter for weighted_vc
    df_wvc = df[df['repair_algorithm'] == 'weighted_vc']
    
    for dataset in ['census', 'compas', 'adult', 'tax']:
        ds_runs = df_wvc[df_wvc['dataset'] == dataset]
        if ds_runs.empty:
            continue
            
        # Take the first run
        row = ds_runs.iloc[0]
        meta_str = row['metadata']
        
        try:
            # Handle potential string wrapping
            if isinstance(meta_str, str):
                if meta_str.startswith("{'"):
                    meta = ast.literal_eval(meta_str)
                else:
                    meta = json.loads(meta_str)
            else:
                meta = meta_str
                
            stats = meta.get('iteration_stats', [])
            if not stats:
                print(f"{dataset}: No iteration stats found.")
                continue
                
            n_iters = len(stats)
            print(f"\n--- Trajectory for {dataset.upper()} (Total Iterations: {n_iters}) ---")
            
            # Print sample points: 0%, 25%, 50%, 75%, 100%
            checkpoints = [0, n_iters//4, n_iters//2, 3*n_iters//4, n_iters-1]
            for i in checkpoints:
                if i < n_iters:
                    s = stats[i]
                    print(f"Iter {i:5d} | Active V: {s.get('n_active', 0):6d} | Hubbiness: {s.get('hubbiness', 0):.4f} | Alpha: {s.get('alpha', 0):.4f}")
                    
        except Exception as e:
            print(f"Error parsing {dataset}: {e}")

if __name__ == "__main__":
    analyze_alpha_trajectory()
