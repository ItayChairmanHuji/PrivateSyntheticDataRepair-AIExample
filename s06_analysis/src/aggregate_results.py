import json
import os
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def aggregate_experiment_2(blueprint_path, results_dir, output_path):
    # 1. Load blueprint
    with open(blueprint_path, 'r') as f:
        blueprint = json.load(f)
    
    jobs = blueprint["jobs"]
    rows = []

    # 2. Iterate over results
    results_path = Path(results_dir)
    exp_dirs = list(results_path.glob("exp_*"))
    
    logger.info(f"Found {len(exp_dirs)} experiment directories.")

    for exp_dir in exp_dirs:
        job_id = exp_dir.name.split("_")[1]
        if job_id not in jobs:
            logger.warning(f"Job ID {job_id} not found in blueprint. Skipping.")
            continue
            
        params = jobs[job_id]
        
        # Find the latest JSON result file
        json_files = list(exp_dir.rglob("result_*.json"))
        if not json_files:
            continue
            
        # Select latest based on file modification time or internal timestamp (here file time is easier)
        json_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_json = json_files[0]
        
        try:
            with open(latest_json, 'r') as f:
                res = json.load(f)
                
            # Flatten metrics
            row = {
                "job_id": job_id,
                "dataset": params["dataset"],
                "synthesizer": params["synthesizer"],
                "epsilon": params["epsilon"],
                "seed": params["seed"],
                "repair_algorithm": params["repair_algorithm"],
                
                # Deletion Ratio
                "deletion_ratio": res.get("deletion_ratio", {}).get("ratio"),
                
                # Marginals Error
                "marginals_error_synthetic": res.get("marginals_error", {}).get("synthetic_avg"),
                "marginals_error_repaired": res.get("marginals_error", {}).get("repaired_avg"),
                
                # TVD
                "tvd_synthetic": res.get("tvd_2way", {}).get("synthetic_avg"),
                "tvd_repaired": res.get("tvd_2way", {}).get("repaired_avg"),
                
                # Violations
                "violations_synthetic": res.get("violations", {}).get("synthetic"),
                "violations_repaired": res.get("violations", {}).get("repaired"),
                
                # Loss Function Components
                "loss_synthetic": res.get("loss_function", {}).get("synthetic", {}).get("total"),
                "loss_repaired": res.get("loss_function", {}).get("repaired", {}).get("total"),
                "loss_marginal_synthetic": res.get("loss_function", {}).get("synthetic", {}).get("marginal_component"),
                "loss_marginal_repaired": res.get("loss_function", {}).get("repaired", {}).get("marginal_component"),
                
                # ML Accuracy (Average of LR, RF, MLP)
                "ml_acc_synthetic": None,
                "ml_acc_repaired": None
            }
            
            # Average ML Accuracy
            ml_syn = res.get("ml_accuracy", {}).get("synthetic", {})
            if ml_syn:
                row["ml_acc_synthetic"] = sum(ml_syn.values()) / len(ml_syn)
                
            ml_rep = res.get("ml_accuracy", {}).get("repaired", {})
            if ml_rep:
                row["ml_acc_repaired"] = sum(ml_rep.values()) / len(ml_rep)
                
            rows.append(row)
        except Exception as e:
            logger.error(f"Error processing {latest_json}: {e}")

    # 3. Create DataFrame and save
    df = pd.DataFrame(rows)
    # Sort for easier viewing
    df = df.sort_values(["dataset", "synthesizer", "epsilon", "repair_algorithm"])
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Aggregated {len(df)} results to {output_path}")

if __name__ == "__main__":
    aggregate_experiment_2(
        blueprint_path="mission_control/blueprints/experiment_2_repair_comparison/blueprint.json",
        results_dir="remote/output/experiment_2_repair_comparison",
        output_path="s06_analysis/output/experiment_2_summary.csv"
    )
