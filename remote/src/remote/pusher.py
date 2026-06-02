import os
import zipfile
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Pusher:
    def __init__(self, remote_host, remote_dir, excludes=None):
        self.remote_host = remote_host
        self.remote_dir = remote_dir
        self.zip_name = "code_sync.zip"
        self.excludes = {
            ".git", ".venv", "__pycache__", "data", "outputs", "old", "models", 
            ".vscode", "remote/output", "s01_loading/input", "s01_loading/output",
            "s02_synthesizing/input", "s02_synthesizing/output",
            "s03_marginals/input", "s03_marginals/output",
            "s04_repairing/input", "s04_repairing/output",
            "s05_evaluating/input", "s05_evaluating/output",
            "s06_analysis/input", "s06_analysis/output", "s06_analysis/notebooks"
        }
        self.excludes.add(self.zip_name)

    def is_excluded(self, path, root_dir):
        rel_path = Path(path).relative_to(root_dir)
        path_str = rel_path.as_posix()
        
        # Check if the path or any of its parents are in excludes
        if path_str in self.excludes:
            return True
        for exclude in self.excludes:
            if path_str.startswith(exclude + "/"):
                return True
        return False

    def create_zip(self, zip_path, root_dir):
        logger.info(f"Creating zip archive: {zip_path}")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(root_dir):
                # Filter directories in-place to prevent os.walk from entering them
                dirs[:] = [d for d in dirs if not self.is_excluded(Path(root) / d, root_dir) and not d.startswith('.')]
                
                for file in files:
                    file_path = Path(root) / file
                    if self.is_excluded(file_path, root_dir) or file.startswith('.'):
                        continue
                    
                    arcname = file_path.relative_to(root_dir).as_posix()
                    
                    # Read content and ensure Unix line endings for scripts
                    if file.endswith('.sh') or file.endswith('.py'):
                        try:
                            with open(file_path, 'rb') as f:
                                content = f.read().replace(b'\r\n', b'\n')
                            zipf.writestr(arcname, content)
                        except Exception as e:
                            logger.error(f"Error processing {file_path}: {e}")
                    else:
                        zipf.write(file_path, arcname)
        logger.info("Zip archive created.")

    def push_paths(self, paths):
        """Push specific files or folders. Folders are zipped."""
        root_dir = Path.cwd()
        
        for p in paths:
            path = Path(p)
            if not path.is_absolute():
                path = root_dir / path
            
            if not path.exists():
                logger.warning(f"Path does not exist: {path}")
                continue

            if path.is_dir():
                zip_name = f"{path.name}.zip"
                zip_path = root_dir / zip_name
                logger.info(f"Zipping folder {path.name} to {zip_name}")
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(path.parent)
                            zipf.write(file_path, arcname)
                
                try:
                    logger.info(f"Pushing zipped folder: {zip_name}")
                    subprocess.run(["scp", str(zip_path), f"{self.remote_host}:{self.remote_dir}/{zip_name}"], check=True)
                    extract_cmd = f"cd {self.remote_dir} && unzip -o {zip_name} && rm {zip_name}"
                    subprocess.run(["ssh", self.remote_host, extract_cmd], check=True)
                finally:
                    if zip_path.exists():
                        os.remove(zip_path)
            else:
                logger.info(f"Pushing file: {path.name}")
                rel_path = path.relative_to(root_dir)
                remote_file_path = f"{self.remote_dir}/{rel_path.as_posix()}"
                remote_parent = f"{self.remote_dir}/{rel_path.parent.as_posix()}"
                
                # Ensure remote directory exists
                subprocess.run(["ssh", self.remote_host, f"mkdir -p {remote_parent}"], check=True)
                subprocess.run(["scp", str(path), f"{self.remote_host}:{remote_file_path}"], check=True)

    def push(self):
        # Assumes project root is parent of 'remote'
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        zip_path = root_dir / self.zip_name
        
        # 1. Create Zip
        self.create_zip(zip_path, root_dir)
        
        if not zip_path.exists():
            raise FileNotFoundError(f"Failed to create zip file at {zip_path}")
        
        try:
            # 2. Upload to remote
            logger.info(f"Uploading {self.zip_name} to {self.remote_host}:{self.remote_dir}")
            subprocess.run(["scp", zip_path.as_posix(), f"{self.remote_host}:{self.remote_dir}/{self.zip_name}"], check=True)
            
            # 3. Extract on remote
            logger.info("Extracting on remote...")
            extract_cmd = f"cd {self.remote_dir} && unzip -o {self.zip_name} && rm {self.zip_name}"
            subprocess.run(["ssh", self.remote_host, extract_cmd], check=True)
            
            logger.info("Successfully pushed code to remote.")
        finally:
            # 4. Cleanup local zip
            if zip_path.exists():
                os.remove(zip_path)
                logger.info("Cleaned up local zip archive.")
