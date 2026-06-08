import subprocess
import os
import zipfile
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class Puller:
    """
    Retrieves results and metrics from the remote cluster.
    """
    def __init__(self, remote_host: str, remote_dir: str):
        self.remote_host = remote_host
        self.remote_dir = remote_dir

    def pull_path(self, remote_rel_path: str, local_dest: Path):
        """
        Pulls a specific path from remote to local.
        """
        remote_path = f"{self.remote_dir}/{remote_rel_path}"
        
        # Check if remote path is a directory
        check_cmd = f"[ -d {remote_path} ] && echo 'dir' || echo 'file'"
        result = subprocess.run(["ssh", self.remote_host, check_cmd], capture_output=True, text=True, check=True)
        is_dir = result.stdout.strip() == 'dir'

        if is_dir:
            zip_name = f"pull_{Path(remote_rel_path).name}.zip"
            remote_zip = f"{self.remote_dir}/{zip_name}"
            
            logger.info(f"Zipping remote folder: {remote_rel_path}")
            zip_cmd = f"cd {self.remote_dir} && zip -r {zip_name} {remote_rel_path}"
            subprocess.run(["ssh", self.remote_host, zip_cmd], check=True)

            try:
                local_zip = local_dest / zip_name
                local_dest.mkdir(parents=True, exist_ok=True)
                
                subprocess.run(["scp", f"{self.remote_host}:{remote_zip}", str(local_zip)], check=True)
                
                with zipfile.ZipFile(local_zip, 'r') as zip_ref:
                    zip_ref.extractall(local_dest)
            finally:
                if (local_dest / zip_name).exists():
                    os.remove(local_dest / zip_name)
                subprocess.run(["ssh", self.remote_host, f"rm {remote_zip}"], check=True)
        else:
            local_dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["scp", f"{self.remote_host}:{remote_path}", str(local_dest)], check=True)
