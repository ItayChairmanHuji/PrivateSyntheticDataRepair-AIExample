import subprocess
import os
import argparse
import shutil
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(cmd, cwd, env=None):
    logger.info(f"Executing: {cmd} in {cwd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd, env=env)

def copy_artifacts(src_dir, dst_dir):
    """Copies all files from src_dir to dst_dir, ensuring dst_dir exists."""
    if not src_dir.exists():
        return
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in os.listdir(src_dir):
        s = src_dir / item
        d = dst_dir / item
        if s.is_dir():
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def create_link(src, dst):
    """Creates a link or copy of src at dst, handled cross-platform."""
    if src.is_dir():
        if os.name == 'nt':
            try:
                subprocess.run(f'mklink /J "{dst}" "{src}"', shell=True, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            os.symlink(src, dst)
    else:
        if os.name == 'nt':
            try:
                os.link(src, dst)
            except OSError:
                shutil.copy2(src, dst)
        else:
            os.symlink(src, dst)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job_id", type=str, required=True, help="Job ID (e.g., 001)")
    parser.add_argument("--blueprint_path", type=str, required=True, help="Path to blueprint.json")
    args = parser.parse_args()
    
    blueprint_path = Path(args.blueprint_path).resolve()
    with open(blueprint_path, 'r') as f:
        blueprint = json.load(f)
    
    if args.job_id not in blueprint["jobs"]:
        logger.error(f"Error: Job ID {args.job_id} not found in blueprint.")
        return

    params = blueprint["jobs"][args.job_id]
    group_name = blueprint["group_name"]
    exp_name = f"exp_{args.job_id}"
    
    logger.info(f"--- Starting Experiment {exp_name} ---")
    
    root = Path(__file__).resolve().parent.parent.parent.parent
    
    # Setup isolated workspace
    tmp_base = Path(os.environ.get("SLURM_TMPDIR", os.environ.get("TEMP", "/tmp")))
    workspace = tmp_base / f"icm_job_{args.job_id}_{os.getpid()}"
    workspace.mkdir(parents=True, exist_ok=True)
    
    try:
        # Setup workspace structure
        stages_needed = ["s01_loading", "s02_synthesizing", "s03_marginals", "s04_repairing", "s05_evaluating"]
        
        # Link core components and stages
        for item in ["data", "shared", "models", "route.py"] + stages_needed:
            src = root / item
            dst = workspace / item
            if not src.exists(): 
                continue
            
            if src.is_dir():
                dst.mkdir(exist_ok=True)
                for subitem in os.listdir(src):
                    # We want fresh input/output for isolation
                    if subitem in ["input", "output", "__pycache__"]:
                        (dst / subitem).mkdir(exist_ok=True)
                    else:
                        create_link(src / subitem, dst / subitem)
            else:
                create_link(src, dst)

        env = os.environ.copy()
        env["PYTHONPATH"] = str(workspace)

        # --- PIPELINE EXECUTION ---
        dataset = params['dataset']
        
        # STAGE 01: Loading
        run_command(f"python s01_loading/src/main.py --config-name={dataset} ++dataset_name={dataset}", workspace, env=env)
        
        # Handoff S1 -> S2
        copy_artifacts(workspace / "s01_loading/output", workspace / "s02_synthesizing/input")

        # STAGE 02: Synthesizing
        s2_final_out = root / "outputs" / group_name / exp_name / "s02_synthesizing"
        if s2_final_out.exists():
            logger.info(f"Skipping Stage 02: found existing results in {s2_final_out}")
            copy_artifacts(s2_final_out, workspace / "s02_synthesizing/output")
        else:
            config_name = params['synthesizer']
            engine = params.get('engine', config_name)
            epsilon = params['epsilon']
            seed = params.get('seed', 42)
            mode = params.get('mode', 'full') 
            size = params.get('sample_size', 50000)
            
            # Determine model path if in sample mode
            model_path_override = ""
            if mode == "sample":
                # Strip suffixes like 100, 1000, 5000 to find base models
                base_dataset = dataset
                for suffix in ["100", "1000", "5000"]:
                    if dataset.endswith(suffix) and dataset != suffix:
                        base_dataset = dataset[:-len(suffix)]
                        break
                
                # Hierarchy: models/{base_dataset}/{algorithm}/{base_dataset}_{algorithm}_eps{epsilon}.pkl
                model_path = Path("models") / base_dataset / engine / f"{base_dataset}_{engine}_eps{epsilon}.pkl"
                model_path_override = f"++model_path={model_path}"
                # For model_loader config, we need to pass these
                run_command(f"python s02_synthesizing/src/main.py --config-name=model_loader ++engine={engine} ++epsilon={epsilon} ++seed={seed} ++dataset_name={dataset} ++mode={mode} {model_path_override} ++size={size}", workspace, env=env)
            else:
                run_command(f"python s02_synthesizing/src/main.py --config-name={config_name} ++engine={engine} ++epsilon={epsilon} ++seed={seed} ++dataset_name={dataset} ++mode={mode}", workspace, env=env)

        # Handoff S1, S2 -> S3
        copy_artifacts(workspace / "s01_loading/output", workspace / "s03_marginals/input")
        copy_artifacts(workspace / "s02_synthesizing/output", workspace / "s03_marginals/input")

        # STAGE 03: Marginals
        # For Experiment 6: use FileObtainer to load pre-generated marginals
        # Hierarchy: final_research/marginals/{dataset}/[random_]marginals.json
        dataset_marginals_dir = root / "marginals" / dataset
        
        # Fallback for canary (adult100) mapping to base dataset (adult) marginals
        if not dataset_marginals_dir.exists():
            base_dataset = dataset
            for suffix in ["100", "1000", "5000"]:
                if dataset.endswith(suffix) and dataset != suffix:
                    base_dataset = dataset[:-len(suffix)]
                    break
            dataset_marginals_dir = root / "marginals" / base_dataset

        # Find any .json file in the marginals dir
        marginals_path = None
        if dataset_marginals_dir.exists():
            json_files = list(dataset_marginals_dir.glob("*.json"))
            if json_files:
                marginals_path = json_files[0]

        if not marginals_path:
            logger.error(f"Error: No marginals found for {dataset} in {dataset_marginals_dir}")
            raise FileNotFoundError(f"Marginals not found for {dataset}")

        run_command(f"python s03_marginals/src/main.py --config-name=from_file ++path={marginals_path} ++dataset_name={dataset}", workspace, env=env)

        # Handoff S1, S2, S3 -> S4
        copy_artifacts(workspace / "s01_loading/output", workspace / "s04_repairing/input")
        copy_artifacts(workspace / "s02_synthesizing/output", workspace / "s04_repairing/input")
        copy_artifacts(workspace / "s03_marginals/output", workspace / "s04_repairing/input")

        # STAGE 04: Repairing
        repairer = params.get('repairer', params.get('repair_algorithm', 'vanilla_vc'))
        repair_args = f"--config-name={repairer} ++dataset_name={dataset}"
        
        # Only pass alpha overrides to weighted_vc to avoid instantiation errors in other repairers
        if repairer == 'weighted_vc':
            if 'use_adaptive_alpha' in params:
                repair_args += f" ++use_adaptive_alpha={params['use_adaptive_alpha']}"
            if 'use_auto_alpha' in params:
                repair_args += f" ++use_auto_alpha={params['use_auto_alpha']}"
            
        run_command(f"python s04_repairing/src/main.py {repair_args}", workspace, env=env)

        # Handoff ALL -> S5
        copy_artifacts(workspace / "s01_loading/output", workspace / "s05_evaluating/input")
        copy_artifacts(workspace / "s02_synthesizing/output", workspace / "s05_evaluating/input")
        copy_artifacts(workspace / "s04_repairing/output", workspace / "s05_evaluating/input")
        copy_artifacts(workspace / "s03_marginals/output", workspace / "s05_evaluating/input")

        # STAGE 05: Evaluating
        run_command(f"python s05_evaluating/src/main.py ++dataset_name={dataset} ++orchestrator.output_dir=s05_evaluating/output/{dataset}", workspace, env=env)

        # --- FINAL COLLECTION ---
        final_dir = root / "outputs" / group_name / exp_name
        final_dir.mkdir(parents=True, exist_ok=True)
        
        for stage in stages_needed:
            stage_out = workspace / stage / "output"
            if stage_out.exists():
                shutil.copytree(stage_out, final_dir / stage, dirs_exist_ok=True)

        logger.info(f"--- Experiment {exp_name} Completed Successfully ---")

    finally:
        shutil.rmtree(workspace)

if __name__ == "__main__":
    main()
