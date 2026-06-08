import os
import zipfile
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DataPusher:
    """
    Syncs essential resources to the remote cluster following RPM rules.
    (Only metadata, configs, and base data; excludes models and large files).
    """
    def __init__(self, remote_host: str, remote_dir: str):
        self.remote_host = remote_host
        self.remote_dir = remote_dir
        self.zip_name = "resources_sync.zip"

    def push_essential_resources(self, root_dir: Path):
        """
        Pushes only .txt, .json, and .md files from r_resources to avoid syncing large datasets/models.
        """
        resources_dir = root_dir / "r_resources"
        if not resources_dir.exists():
            logger.warning("No r_resources directory found locally.")
            return

        zip_path = root_dir / self.zip_name
        
        logger.info(f"Creating resource zip archive: {zip_path}")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(resources_dir):
                root_path = Path(root)
                for file in files:
                    if file.endswith('.txt') or file.endswith('.json') or file.endswith('.md'):
                        file_path = root_path / file
                        # Keep the r_resources prefix in the archive
                        arcname = file_path.relative_to(root_dir).as_posix()
                        zipf.write(file_path, arcname)

        remote_resources_dir = f"{self.remote_dir}/r_resources"
        
        try:
            # Ensure remote base directory exists
            subprocess.run(["ssh", self.remote_host, f"mkdir -p {self.remote_dir}"], check=True)
            
            logger.info("Uploading essential metadata and configs...")
            subprocess.run(["scp", str(zip_path), f"{self.remote_host}:{self.remote_dir}/{self.zip_name}"], check=True)

            logger.info("Extracting on remote...")
            extract_cmd = f"cd {self.remote_dir} && unzip -o {self.zip_name} && rm {self.zip_name}"
            subprocess.run(["ssh", self.remote_host, extract_cmd], check=True)
            
            logger.info("Successfully pushed essential resources.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to push essential resources: {e}")
            raise
        finally:
            if zip_path.exists():
                os.remove(zip_path)

