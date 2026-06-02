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
            array_ranges = ["1"]
            logger.info("Running CANARY job only (index 1).")
        else:
            # Split into chunks of 1000 to respect MaxArraySize
            chunk_size = 1000
            array_ranges = []
            for i in range(1, total_jobs + 1, chunk_size):
                end = min(i + chunk_size - 1, total_jobs)
                array_ranges.append(f"{i}-{end}")
            logger.info(f"Submitting {len(array_ranges)} batches for total {total_jobs} jobs.")
        
        for array_range in array_ranges:
            start_idx = int(array_range.split("-")[0])
            offset = start_idx - 1
            # Adjust array range to be 1-based relative to 1
            relative_end = int(array_range.split("-")[1]) - offset
            relative_range = f"1-{relative_end}"
            
            logger.info(f"Submitting array: {relative_range} with offset: {offset}")
            # Updated path to slurm_array.sh and added job-name for easier scancel
            sbatch_cmd = f"sbatch --job-name={blueprint_name} --array={relative_range} remote/src/remote/slurm_array.sh {blueprint_name} {offset}"
            self.run_remote_command(sbatch_cmd)
        
        logger.info("--- Deployment Successful ---")
        logger.info(f"Monitor jobs with: ssh {self.remote_host} 'squeue -u $USER'")

    def rerun(self, blueprint_name):
        logger.info(f"--- RERUN: Starting rerun for {blueprint_name} ---")
        
        # 1. Push latest code
        logger.info("--- Step 1: Pushing latest code/config ---")
        self.pusher.push()

        # 2. Cancel existing jobs for this blueprint
        logger.info(f"--- Step 2: Cancelling existing jobs for {blueprint_name} ---")
        try:
            self.run_remote_command(f"scancel --name={blueprint_name}")
        except Exception as e:
            logger.warning(f"Could not cancel jobs (they might not exist): {e}")

        # 3. Remove remote outputs for this blueprint
        logger.info(f"--- Step 3: Cleaning remote outputs for {blueprint_name} ---")
        # Ensure we only delete outputs/blueprint_name to avoid accidents
        clean_cmd = f"rm -rf outputs/{blueprint_name}"
        self.run_remote_command(clean_cmd)

        # 4. Deploy again
        logger.info("--- Step 4: Resubmitting experiment ---")
        self.deploy(blueprint_name)
        
        logger.info(f"--- RERUN: {blueprint_name} successfully resubmitted ---")
