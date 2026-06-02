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
        logger.info(f"Executing: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        subprocess.run(cmd, shell=False, check=True)

    def pull_paths(self, paths):
        """Pull specific files or folders. Folders are zipped on remote."""
        root_dir = Path.cwd()
        
        for p in paths:
            # Check if path exists on remote and if it's a directory
            check_cmd = f"[ -d {self.remote_dir}/{p} ] && echo 'dir' || echo 'file'"
            result = subprocess.run(["ssh", self.remote_host, check_cmd], capture_output=True, text=True, check=True)
            is_dir = result.stdout.strip() == 'dir'
            
            if is_dir:
                zip_name = f"{Path(p).name}.zip"
                remote_zip = f"{self.remote_dir}/{zip_name}"
                local_zip = root_dir / zip_name
                
                logger.info(f"Zipping remote folder: {p}")
                zip_cmd = f"cd {self.remote_dir} && zip -r {zip_name} {p}"
                self.run_command(["ssh", self.remote_host, zip_cmd])
                
                try:
                    logger.info(f"Pulling zipped folder: {zip_name}")
                    self.run_command(["scp", f"{self.remote_host}:{remote_zip}", str(local_zip)])
                    
                    logger.info(f"Extracting {zip_name} locally...")
                    import zipfile
                    with zipfile.ZipFile(local_zip, 'r') as zip_ref:
                        zip_ref.extractall(root_dir)
                finally:
                    if local_zip.exists():
                        os.remove(local_zip)
                    self.run_command(["ssh", self.remote_host, f"rm {remote_zip}"])
            else:
                logger.info(f"Pulling file: {p}")
                local_path = root_dir / p
                local_path.parent.mkdir(parents=True, exist_ok=True)
                self.run_command(["scp", f"{self.remote_host}:{self.remote_dir}/{p}", str(local_path)])

    def pull(self, experiment_group, use_zip=True, exp_ids=None, stats_only=False):
        root = Path(__file__).resolve().parent.parent.parent.parent
        local_output_base = root / "outputs" / experiment_group
        local_output_base.mkdir(parents=True, exist_ok=True)

        logger.info(f"--- Step 1: Syncing '{experiment_group}' from {self.remote_host} ---")
        
        if use_zip:
            zip_name = f"{experiment_group}_results.zip"
            remote_zip = f"{self.remote_dir}/{zip_name}"
            
            # Construct target path(s) for zipping
            if exp_ids:
                targets = [f"outputs/{experiment_group}/exp_{str(eid).zfill(3)}" for eid in exp_ids]
                target_str = " ".join(targets)
                logger.info(f"Zipping specific results on remote: {exp_ids}")
            else:
                target_str = f"outputs/{experiment_group}"
                logger.info(f"Zipping all results on remote for group: {experiment_group}")

            # 1. Zip on remote
            if stats_only:
                logger.info("Using 'stats_only' mode (pulling only JSON evaluation files and repair metadata)")
                # Include result_*.json from s05 and metadata.json from s04
                remote_cmd = f"cd {self.remote_dir} && (find {target_str} -name 'result_*.json' -o -path '*/s04_repairing/*/metadata.json') | zip {zip_name} -@"
            else:
                remote_cmd = f"cd {self.remote_dir} && zip -r {zip_name} {target_str}"
            
            self.run_command(["ssh", self.remote_host, remote_cmd])
            
            # 2. Pull zip
            logger.info(f"Pulling {zip_name}...")
            self.run_command(["scp", f"{self.remote_host}:{remote_zip}", str(root / zip_name)])
            
            # 3. Unzip locally
            logger.info(f"Extracting {zip_name} locally...")
            import zipfile
            with zipfile.ZipFile(root / zip_name, 'r') as zip_ref:
                zip_ref.extractall(root)
                
            # 4. Cleanup
            os.remove(root / zip_name)
            self.run_command(["ssh", self.remote_host, f"rm {remote_zip}"])
        else:
            # Fallback to rsync
            remote_path = f"{self.remote_host}:{self.remote_dir}/outputs/{experiment_group}/"
            local_path = f"{local_output_base}/"
            try:
                self.run_command(["rsync", "-avzP", remote_path, local_path])
            except Exception:
                logger.warning("rsync failed or not found, falling back to scp...")
                self.run_command(["scp", "-r", f"{remote_path}*", local_path])

        logger.info(f"--- Step 2: Aggregating Results ---")
        all_results = []
        
        # Walk through the local synced directory to find all .json results
        for exp_dir in local_output_base.iterdir():
            if exp_dir.is_dir() and exp_dir.name.startswith("exp_"):
                job_id = exp_dir.name.split("_")[1]
                
                # Try to get repair stats from s04
                repair_metadata = {}
                repair_dir = exp_dir / "s04_repairing"
                if repair_dir.exists():
                    for meta_file in repair_dir.rglob("metadata.json"):
                        try:
                            with open(meta_file, 'r') as f:
                                repair_metadata = json.load(f)
                        except Exception as e:
                            logger.error(f"Error reading repair metadata {meta_file}: {e}")

                # Check s05_evaluating subfolder
                eval_dir = exp_dir / "s05_evaluating"
                if eval_dir.exists():
                    for result_file in eval_dir.rglob("result_*.json"):
                        try:
                            with open(result_file, 'r') as f:
                                data = json.load(f)
                                data["job_id"] = job_id
                                
                                # Merge repair metadata into result metadata
                                if "metadata" not in data:
                                    data["metadata"] = {}
                                
                                if repair_metadata:
                                    data["metadata"].update(repair_metadata)
                                    
                                    # Also provide top-level means for convenience if needed, 
                                    # though flattener re-calculates them
                                    if "iteration_stats" in repair_metadata:
                                        stats = pd.DataFrame(repair_metadata["iteration_stats"])
                                        data["mean_alpha"] = stats["alpha"].mean()
                                        data["mean_connectivity"] = stats["connectivity"].mean()
                                        data["mean_hubbiness"] = stats["hubbiness"].mean()

                                all_results.append(data)
                        except Exception as e:
                            logger.error(f"Error reading {result_file}: {e}")

        if all_results:
            df = pd.DataFrame(all_results)
            
            # Deduplicate by job_id, keeping the latest timestamp
            if "timestamp" in df.columns:
                df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp_dt', ascending=False).drop_duplicates('job_id')
                df = df.drop(columns=['timestamp_dt'])
                logger.info(f"Deduplicated results: kept {len(df)} latest results from {len(all_results)} total found.")

            # Load blueprint to join labels
            blueprint_path = root / "mission_control" / "blueprints" / experiment_group / "blueprint.json"
            if blueprint_path.exists():
                try:
                    with open(blueprint_path, 'r') as f:
                        blueprint = json.load(f)
                    
                    blueprint_df = pd.DataFrame.from_dict(blueprint["jobs"], orient='index')
                    blueprint_df.index.name = 'job_id'
                    blueprint_df = blueprint_df.reset_index()
                    
                    # Merge
                    df = df.merge(blueprint_df, on='job_id', suffixes=('', '_bp'))
                    logger.info("Successfully merged with blueprint labels.")
                except Exception as e:
                    logger.error(f"Error merging with blueprint: {e}")
            
            # Standardized summary path in remote/output
            summary_path = root / "remote" / "output" / f"{experiment_group}_summary.csv"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(summary_path, index=False)
            logger.info(f"Successfully aggregated {len(all_results)} results into {summary_path}")
        else:
            logger.info("No results found to aggregate.")
