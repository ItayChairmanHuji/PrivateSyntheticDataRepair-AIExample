import os
import zipfile
import subprocess
import logging
from pathlib import Path
from typing import List, Set

logger = logging.getLogger(__name__)

class Pusher:
    """
    Syncs local code and configs to the remote cluster.
    """
    DEFAULT_EXCLUDES = {
        ".git", ".venv", "__pycache__", ".pytest_cache", ".vscode",
        "old", "r_resources", "outputs", "models", "synthetic_data",
        "code_sync.zip", "*.tar", "*.tar.gz", "*.zip", "*.pkl"
    }

    def __init__(self, remote_host: str, remote_dir: str, excludes: Set[str] = None):
        self.remote_host = remote_host
        self.remote_dir = remote_dir
        self.excludes = self.DEFAULT_EXCLUDES.union(excludes or set())
        self.zip_name = "code_sync.zip"

    def _is_excluded(self, path: Path, root_dir: Path) -> bool:
        try:
            rel_path = path.relative_to(root_dir)
        except ValueError:
            return False
            
        path_parts = rel_path.parts
        if not path_parts:
            return False
            
        # Check if any part of the path is in excludes (exact match or glob)
        for part in path_parts:
            if part.startswith('.') and part != '.':
                return True
            for exclude in self.excludes:
                if part == exclude or path.name == exclude or path.match(exclude):
                    return True
        return False

    def create_zip(self, zip_path: Path, root_dir: Path):
        logger.info(f"Creating zip archive: {zip_path}")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(root_dir):
                root_path = Path(root)
                
                # Filter directories in-place to prevent os.walk from entering them
                dirs[:] = [d for d in dirs if not self._is_excluded(root_path / d, root_dir)]

                for file in files:
                    file_path = root_path / file
                    if self._is_excluded(file_path, root_dir):
                        continue

                    arcname = file_path.relative_to(root_dir).as_posix()

                    # Handle line endings for scripts
                    if file.endswith('.sh') or file.endswith('.py'):
                        try:
                            with open(file_path, 'rb') as f:
                                content = f.read().replace(b'\r\n', b'\n')
                            zipf.writestr(arcname, content)
                        except Exception as e:
                            logger.error(f"Error processing {file_path}: {e}")
                    else:
                        zipf.write(file_path, arcname)

    def push(self, root_dir: Path):
        zip_path = root_dir / self.zip_name
        self.create_zip(zip_path, root_dir)

        try:
            # Ensure remote directory exists
            subprocess.run(["ssh", self.remote_host, f"mkdir -p {self.remote_dir}"], check=True)
            
            # Upload
            subprocess.run(["scp", str(zip_path), f"{self.remote_host}:{self.remote_dir}/{self.zip_name}"], check=True)

            # Extract and Cleanup
            extract_cmd = f"cd {self.remote_dir} && unzip -o {self.zip_name} && rm {self.zip_name}"
            subprocess.run(["ssh", self.remote_host, extract_cmd], check=True)
            
            logger.info("Successfully pushed codebase to remote.")
        finally:
            if zip_path.exists():
                os.remove(zip_path)
