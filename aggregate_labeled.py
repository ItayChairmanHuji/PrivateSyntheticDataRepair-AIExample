import json
import pandas as pd
from pathlib import Path

def aggregate_labeled(experiment_group):
    root = Path.cwd()
    local_output_base = root / "outputs" / experiment_group
    all_results = []
    
    if not local_output_base.exists():
        print(f"Error: {local_output_base} does not exist")
        return

    print(f"Scanning {local_output_base} for results...")
    for exp_dir in local_output_base.iterdir():
        if exp_dir.is_dir() and exp_dir.name.startswith("exp_"):
            job_id = exp_dir.name.split("_")[1]
            eval_dir = exp_dir / "s05_evaluating"
            if eval_dir.exists():
                for result_file in eval_dir.rglob("result_*.json"):
                    try:
                        with open(result_file, 'r') as f:
                            data = json.load(f)
                            data["job_id"] = job_id
                            all_results.append(data)
                    except Exception as e:
                        print(f"Error reading {result_file}: {e}")

    if all_results:
        df = pd.DataFrame(all_results)
        
        # Load blueprint to join labels
        blueprint_path = root / "mission_control" / "blueprints" / experiment_group / "blueprint.json"
        if blueprint_path.exists():
            with open(blueprint_path, 'r') as f:
                blueprint = json.load(f)
            
            blueprint_df = pd.DataFrame.from_dict(blueprint["jobs"], orient='index')
            blueprint_df.index.name = 'job_id'
            blueprint_df = blueprint_df.reset_index()
            
            # Merge
            df = df.merge(blueprint_df, on='job_id', suffixes=('', '_bp'))
            print("Successfully merged with blueprint labels.")
        
        summary_path = root / "remote" / "output" / f"{experiment_group}_labeled.csv"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(summary_path, index=False)
        print(f"Successfully aggregated {len(all_results)} results into {summary_path}")
    else:
        print("No results found to aggregate.")

if __name__ == "__main__":
    aggregate_labeled("experiment_4_repair_comparison")
