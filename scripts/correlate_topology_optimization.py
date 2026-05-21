import pandas as pd
import numpy as np
import os

# Paths
EXPERIMENTS_PATH = "experiments_alpha_eps01_b1000_abserr.csv"
TOPOLOGY_PATH = "outputs/graph_topology_summary.csv"

def analyze_correlations():
    # 1. Load Data
    if not os.path.exists(EXPERIMENTS_PATH):
        print(f"Error: {EXPERIMENTS_PATH} not found.")
        return
    
    df_exp = pd.read_csv(EXPERIMENTS_PATH)
    
    # Use standard type command to read topology if it's ignored, but here we assume it's accessible to Python
    try:
        df_topo = pd.read_csv(TOPOLOGY_PATH)
    except Exception as e:
        print(f"Error reading topology cache: {e}")
        return

    # 2. Find Optimal Alpha per (dataset, synthesizer)
    # We focus on Eps 0.1 as that matches our fine-grained sweep
    # For synthesizer, the experiments CSV uses 'engine' or 'synthesizer'
    
    # Filter for Epsilon 0.1 results (they are the ones with fine-grained alpha)
    # Note: The experiments file might contain other epsilons if aggregated, but the current focus is the sweep
    
    # Define "Optimal" as minimizing loss_function_repaired_total
    # If loss_function_repaired_total is NaN, we might need a fallback
    
    results = []
    
    groups = df_exp.groupby(['dataset', 'engine'])
    for (dataset, engine), group in groups:
        # Sort by alpha
        group = group.sort_values('meta_repairer_params_alpha')
        
        # Find index of minimum loss
        if group['loss_function_repaired_total'].isnull().all():
            # Fallback: balance marginal error and deletion ratio manually if needed
            # For now, just skip or use another metric
            continue
            
        idx_opt = group['loss_function_repaired_total'].idxmin()
        opt_alpha = group.loc[idx_opt, 'meta_repairer_params_alpha']
        min_loss = group.loc[idx_opt, 'loss_function_repaired_total']
        
        # Also capture the "error cliff" - where marginal error increases by more than 10x
        group['error_ratio'] = group['marginals_error_repaired_avg'] / group['marginals_error_repaired_avg'].shift(1)
        cliff_alpha = group[group['error_ratio'] > 10]['meta_repairer_params_alpha'].min()
        
        results.append({
            'dataset': dataset,
            'algorithm': engine,
            'opt_alpha': opt_alpha,
            'min_loss': min_loss,
            'cliff_alpha': cliff_alpha,
            'max_accuracy': group['ml_accuracy_repaired_logistic_regression'].max(),
            'min_error': group['marginals_error_repaired_avg'].min()
        })
        
    df_opt = pd.DataFrame(results)
    
    # 3. Merge with Topology (at Eps 0.1)
    df_topo_01 = df_topo[df_topo['eps'] == 0.1].copy()
    
    df_merged = pd.merge(df_opt, df_topo_01, on=['dataset', 'algorithm'], how='inner')
    
    if df_merged.empty:
        print("Warning: Merged dataframe is empty. Check dataset/algorithm naming consistency.")
        print("Opt keys:", df_opt[['dataset', 'algorithm']].values)
        print("Topo keys:", df_topo_01[['dataset', 'algorithm']].values)
        return

    # 4. Calculate Correlations
    print("\n--- Correlation Analysis (Optimal Alpha vs Topology) ---")
    metrics = ['n_edges', 'max_degree', 'mean_degree_active', 'hub_coverage_top_1pct', 'giant_comp_size']
    
    correlations = {}
    for metric in metrics:
        if metric in df_merged.columns:
            corr = df_merged['opt_alpha'].corr(df_merged[metric])
            correlations[metric] = corr
            print(f"Correlation (opt_alpha vs {metric}): {corr:.4f}")

    print("\n--- Correlation Analysis (Cliff Alpha vs Topology) ---")
    for metric in metrics:
        if metric in df_merged.columns and not df_merged['cliff_alpha'].isnull().all():
            corr = df_merged['cliff_alpha'].corr(df_merged[metric])
            print(f"Correlation (cliff_alpha vs {metric}): {corr:.4f}")

    # 5. Output Summary Table
    print("\n--- Merged Data Summary ---")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_merged[['dataset', 'algorithm', 'opt_alpha', 'cliff_alpha', 'hub_coverage_top_1pct', 'max_degree']])
    
    # Debug correlations: check for constant values
    print("\nValue counts for opt_alpha:")
    print(df_merged['opt_alpha'].value_counts())
    
    print("\nValue counts for cliff_alpha:")
    print(df_merged['cliff_alpha'].value_counts())
    
    df_merged.to_csv("outputs/topology_correlation_results.csv", index=False)
    print("\nResults saved to outputs/topology_correlation_results.csv")

if __name__ == "__main__":
    analyze_correlations()
