import subprocess
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Deployer:
    def __init__(self, remote_host, remote_dir, pusher):
        self.remote_host = remote_host
        self.remote_dir = remote_dir
        self.pusher = pusher

    def run_remote_command(self, cmd):
        logger.info(f"Executing on {self.remote_host}: {cmd}")
        subprocess.run(["ssh", self.remote_host, f"cd {self.remote_dir} && {cmd}"], check=True)

    def deploy(self, blueprint_name, canary_only=False):
        # 1. Sync Code
        logger.info("--- Step 1: Synchronizing Code ---")
        self.pusher.push()
        
        # 2. Prepare Remote Folders
        logger.info("--- Step 2: Preparing Remote Environment ---")
        self.run_remote_command("mkdir -p remote/output/logs")
        
        # 3. Read Blueprint to get total jobs
        # Blueprint should be in remote/input/ (routed from s00 or mission_control)
        root = Path(__file__).resolve().parent.parent.parent.parent
        blueprint_local_path = root / "remote" / "input" / blueprint_name / "blueprint.json"
        
        if not blueprint_local_path.exists():
            # Fallback to mission_control if not found in remote/input
            blueprint_local_path = root / "mission_control" / "blueprints" / blueprint_name / "blueprint.json"
            
        if not blueprint_local_path.exists():
            logger.error(f"Error: Blueprint {blueprint_name} not found.")
            return
        
        with open(blueprint_local_path, "r") as f:
            blueprint = json.load(f)
        
        total_jobs = blueprint["total_jobs"]
        logger.info(f"Blueprint '{blueprint_name}' has {total_jobs} jobs.")
        
        # 4. Submit Slurm Job
        logger.info("--- Step 3: Submitting Slurm Job ---")
        if canary_only:
            array_range = "1"
            logger.info("Running CANARY job only (index 1).")
        else:
            array_range = f"1-{total_jobs}"
            logger.info(f"Submitting full array: {array_range}")
        
        # Updated path to slurm_array.sh
        sbatch_cmd = f"sbatch --array={array_range} remote/src/remote/slurm_array.sh {blueprint_name}"
        self.run_remote_command(sbatch_cmd)
        
        logger.info("--- Deployment Successful ---")
        logger.info(f"Monitor jobs with: ssh {self.remote_host} 'squeue -u $USER'")
