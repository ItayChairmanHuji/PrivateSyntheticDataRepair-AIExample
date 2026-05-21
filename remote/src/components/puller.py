import subprocess
import os
import json
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Puller:
    def __init__(self, remote_host, remote_dir):
        self.remote_host = remote_host
        self.remote_dir = remote_dir

    def run_command(self, cmd):
        logger.info(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    def pull(self, experiment_group, use_zip=True):
        root = Path(__file__).resolve().parent.parent.parent.parent
        local_output_base = root / "outputs" / experiment_group
        local_output_base.mkdir(parents=True, exist_ok=True)

        logger.info(f"--- Step 1: Syncing '{experiment_group}' from {self.remote_host} ---")
        
        if use_zip:
            zip_name = f"{experiment_group}_results.zip"
            remote_zip = f"{self.remote_dir}/{zip_name}"
            
            # 1. Zip on remote
            logger.info(f"Zipping results on remote: {remote_zip}")
            zip_cmd = f"ssh {self.remote_host} 'cd {self.remote_dir} && zip -r {zip_name} outputs/{experiment_group}'"
            self.run_command(zip_cmd)
            
            # 2. Pull zip
            logger.info(f"Pulling {zip_name}...")
            pull_cmd = f"scp {self.remote_host}:{remote_zip} {root}/{zip_name}"
            self.run_command(pull_cmd)
            
            # 3. Unzip locally
            logger.info(f"Extracting {zip_name} locally...")
            import zipfile
            with zipfile.ZipFile(root / zip_name, 'r') as zip_ref:
                zip_ref.extractall(root)
                
            # 4. Cleanup
            os.remove(root / zip_name)
            self.run_command(f"ssh {self.remote_host} 'rm {remote_zip}'")
        else:
            # Fallback to rsync
            remote_path = f"{self.remote_host}:{self.remote_dir}/outputs/{experiment_group}/"
            local_path = f"{local_output_base}/"
            try:
                rsync_cmd = f"rsync -avzP {remote_path} {local_path}"
                self.run_command(rsync_cmd)
            except Exception:
                logger.warning("rsync failed or not found, falling back to scp...")
                scp_cmd = f"scp -r {remote_path}* {local_path}"
                self.run_command(scp_cmd)

        logger.info(f"--- Step 2: Aggregating Results ---")
        all_results = []
        
        # Walk through the local synced directory to find all .json results
        for exp_dir in local_output_base.iterdir():
            if exp_dir.is_dir() and exp_dir.name.startswith("exp_"):
                # Check s05_evaluating subfolder
                eval_dir = exp_dir / "s05_evaluating"
                if eval_dir.exists():
                    for result_file in eval_dir.rglob("result_*.json"):
                        try:
                            with open(result_file, 'r') as f:
                                data = json.load(f)
                                all_results.append(data)
                        except Exception as e:
                            logger.error(f"Error reading {result_file}: {e}")

        if all_results:
            df = pd.DataFrame(all_results)
            # Standardized summary path in remote/output
            summary_path = root / "remote" / "output" / f"{experiment_group}_summary.csv"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(summary_path, index=False)
            logger.info(f"Successfully aggregated {len(all_results)} results into {summary_path}")
        else:
            logger.info("No results found to aggregate.")
