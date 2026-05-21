import subprocess
import os
import argparse
import shutil
import json
from pathlib import Path

def run_command(cmd, cwd, env=None):
    print(f"Executing: {cmd} in {cwd}")
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
            # On Windows, use junctions for directories if possible, otherwise copy
            try:
                subprocess.run(f'mklink /J "{dst}" "{src}"', shell=True, check=True, capture_output=True)
            except subprocess.CalledProcessError:
                shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            os.symlink(src, dst)
    else:
        if os.name == 'nt':
            # On Windows, symlinking files requires privileges, so we'll just copy for now
            # Alternatively, use hardlinks: os.link(src, dst)
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
        print(f"Error: Job ID {args.job_id} not found in blueprint.")
        return

    params = blueprint["jobs"][args.job_id]
    group_name = blueprint["group_name"]
    exp_name = f"exp_{args.job_id}"
    
    print(f"--- Starting Experiment {exp_name} (Training Only) ---")
    print(f"Parameters: {params}")
    
    root = Path(__file__).resolve().parent.parent.parent
    
    # Setup isolated workspace
    tmp_base = Path(os.environ.get("SLURM_TMPDIR", os.environ.get("TEMP", "/tmp")))
    workspace = tmp_base / f"icm_job_{args.job_id}_{os.getpid()}"
    workspace.mkdir(parents=True, exist_ok=True)
    
    try:
        # 1. Setup workspace structure (links to code, fresh input/output dirs)
        # We only need S1 and S2 for this experiment.
        # We EXCLUDE .venv as it's huge and usually managed by the environment.
        stages_needed = ["s01_loading", "s02_synthesizing"]
        for item in ["data", "shared", "route.py"] + stages_needed:
            src = root / item
            dst = workspace / item
            if not src.exists(): continue
            
            if src.is_dir():
                dst.mkdir(exist_ok=True)
                for subitem in os.listdir(src):
                    if subitem in ["input", "output", "__pycache__"]:
                        (dst / subitem).mkdir(exist_ok=True)
                    else:
                        create_link(src / subitem, dst / subitem)
            else:
                create_link(src, dst)
        
        # Ensure 'models' directory exists in workspace (symlink to actual root models to persist)
        (workspace / "models").mkdir(exist_ok=True)
        # We want the models to persist beyond the workspace cleanup
        # So we use the root models dir
        # workspace_models = workspace / "models"
        # root_models = root / "models"
        # But wait, if multiple jobs write to root/models, we might have issues if filenames collide.
        # However, model names include dataset, engine, and epsilon, so they are unique.

        env = os.environ.copy()
        env["PYTHONPATH"] = str(workspace)

        # STAGE 01: Loading
        run_command(f"python s01_loading/src/main.py --config-name={params['dataset']}", workspace, env=env)
        
        # Handoff S1 -> S2
        copy_artifacts(workspace / "s01_loading/output", workspace / "s02_synthesizing/input")

        # STAGE 02: Training (Mode: train, using model_trainer)
        engine = params['synthesizer']
        epsilon = params['epsilon']
        save_path = str(root / "models")
        # Use '+' for 'mode' (new), regular for 'save_path' (existing)
        run_command(f"python s02_synthesizing/src/main.py --config-name=model_trainer engine={engine} epsilon={epsilon} +mode=train save_path={save_path}", workspace, env=env)

        # --- FINAL COLLECTION (Trace) ---
        final_dir = root / "outputs" / group_name / exp_name
        final_dir.mkdir(parents=True, exist_ok=True)
        
        for stage in stages_needed:
            stage_out = workspace / stage / "output"
            if stage_out.exists():
                shutil.copytree(stage_out, final_dir / stage, dirs_exist_ok=True)

        print(f"--- Experiment {exp_name} Completed Successfully ---")
        print(f"Full trace saved to: {final_dir}")
        print(f"Model saved to: {save_path}")

    finally:
        shutil.rmtree(workspace)

if __name__ == "__main__":
    main()
