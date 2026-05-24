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
        engine = params['synthesizer']
        epsilon = params['epsilon']
        seed = params.get('seed', 42)
        mode = params.get('mode', 'full') 
        size = params.get('sample_size', 50000)
        
        # Determine model path if in sample mode
        model_path_override = ""
        if mode == "sample":
            # Hierarchy: models/{dataset}/{algorithm}/{dataset}_{algorithm}_eps{epsilon}.pkl
            model_path = Path("models") / dataset / engine / f"{dataset}_{engine}_eps{epsilon}.pkl"
            model_path_override = f"++model_path={model_path}"
            # For model_loader config, we need to pass these
            run_command(f"python s02_synthesizing/src/main.py --config-name=model_loader ++engine={engine} ++epsilon={epsilon} ++seed={seed} ++dataset_name={dataset} ++mode={mode} {model_path_override} ++size={size}", workspace, env=env)
        else:
            run_command(f"python s02_synthesizing/src/main.py --config-name={engine} ++engine={engine} ++epsilon={epsilon} ++seed={seed} ++dataset_name={dataset} ++mode={mode}", workspace, env=env)

        # Handoff S1, S2 -> S3
        copy_artifacts(workspace / "s01_loading/output", workspace / "s03_marginals/input")
        copy_artifacts(workspace / "s02_synthesizing/output", workspace / "s03_marginals/input")

        # STAGE 03: Marginals
        run_command(f"python s03_marginals/src/main.py ++dataset_name={dataset}", workspace, env=env)

        # Handoff S1, S2, S3 -> S4
        copy_artifacts(workspace / "s01_loading/output", workspace / "s04_repairing/input")
        copy_artifacts(workspace / "s02_synthesizing/output", workspace / "s04_repairing/input")
        copy_artifacts(workspace / "s03_marginals/output", workspace / "s04_repairing/input")

        # STAGE 04: Repairing
        repairer = params.get('repairer', params.get('repair_algorithm', 'vanilla_vc'))
        repair_args = f"--config-name={repairer} ++dataset_name={dataset}"
        if repairer == "weighted_vc":
            repair_args += " ++use_adaptive_alpha=True"
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
