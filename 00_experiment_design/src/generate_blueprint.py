import yaml
import json
import os
import argparse
from pathlib import Path
from itertools import product

def generate_blueprint(template_path, output_dir):
    with open(template_path, 'r') as f:
        template = yaml.safe_load(f)
    
    group_name = template.get('experiment_group', 'default_group')
    base_config = template.get('base_config', {})
    sweep_params = template.get('sweep_parameters', {})
    
    # Generate all combinations of parameters
    keys = list(sweep_params.keys())
    values = list(sweep_params.values())
    combinations = list(product(*values))
    
    group_dir = Path(output_dir) / group_name
    os.makedirs(group_dir, exist_ok=True)
    
    blueprint_summary = {
        "group_name": group_name,
        "total_jobs": len(combinations),
        "jobs": {}
    }
    
    for i, combo in enumerate(combinations):
        job_id = f"{i+1:03d}"
        job_params = dict(zip(keys, combo))
        
        # Merge base config with sweep params
        full_config = base_config.copy()
        for key, value in job_params.items():
            # Handle nested keys if needed (simplified here)
            full_config[key] = value
        
        job_dir = group_dir / f"exp_{job_id}"
        os.makedirs(job_dir, exist_ok=True)
        
        with open(job_dir / "config.yaml", 'w') as f:
            yaml.dump(full_config, f)
            
        blueprint_summary["jobs"][job_id] = job_params
    
    with open(group_dir / "blueprint.json", 'w') as f:
        json.dump(blueprint_summary, f, indent=2)
        
    print(f"Generated blueprint for '{group_name}' with {len(combinations)} jobs in {group_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="icm_sandbox/00_experiment_design/output")
    args = parser.parse_args()
    generate_blueprint(args.template, args.output_dir)
