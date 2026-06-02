import json
import pandas as pd
from pathlib import Path

def evaluate_census_results():
    exp_dir = Path("outputs/experiment_7_repair_comparison/exp_466")
    
    # Check the evaluation results json
    eval_file = exp_dir / "s05_evaluating/census/default_experiment"
    eval_json = list(eval_file.glob("*.json"))
    if eval_json:
        with open(eval_json[0], 'r') as f:
            data = json.load(f)
            
        print("--- Census Evaluation Metrics (Before Fix) ---")
        print(f"Marginals Error (Synthetic): {data.get('marginals_error', {}).get('synthetic_avg', 'N/A')}")
        print(f"Marginals Error (Repaired): {data.get('marginals_error', {}).get('repaired_avg', 'N/A')}")
        print(f"TVD 2-way (Synthetic): {data.get('tvd_2way', {}).get('synthetic_avg', 'N/A')}")
        print(f"TVD 2-way (Repaired): {data.get('tvd_2way', {}).get('repaired_avg', 'N/A')}")
    else:
        print("No evaluation JSON found for census.")

if __name__ == "__main__":
    evaluate_census_results()
