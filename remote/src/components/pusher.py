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
        self.excludes = excludes or {
            ".git", ".venv", "__pycache__", "data", "outputs", "old", "models", 
            ".vscode", "remote/output"
        }
        self.excludes.add(self.zip_name)

    def create_zip(self, zip_path, root_dir):
        logger.info(f"Creating zip archive: {zip_path}")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(root_dir):
                # Filter directories
                dirs[:] = [d for d in dirs if d not in self.excludes and not d.startswith('.')]
                
                for file in files:
                    if file in self.excludes or file.startswith('.'):
                        continue
                    
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(root_dir)
                    
                    # Check if any parent directory is in EXCLUDES
                    if any(part in self.excludes for part in arcname.parts):
                        continue
                    
                    # Read content and ensure Unix line endings for scripts
                    if file.endswith('.sh') or file.endswith('.py'):
                        try:
                            with open(file_path, 'rb') as f:
                                content = f.read().replace(b'\r\n', b'\n')
                            zipf.writestr(str(arcname), content)
                        except Exception as e:
                            logger.error(f"Error processing {file_path}: {e}")
                    else:
                        zipf.write(file_path, arcname)
        logger.info("Zip archive created.")

    def push(self):
        # Assumes project root is parent of 'remote'
        root_dir = Path(__file__).resolve().parent.parent.parent.parent
        zip_path = root_dir / self.zip_name
        
        # 1. Create Zip
        self.create_zip(zip_path, root_dir)
        
        try:
            # 2. Upload to remote
            logger.info(f"Uploading {self.zip_name} to {self.remote_host}:{self.remote_dir}")
            subprocess.run(["scp", str(zip_path), f"{self.remote_host}:{self.remote_dir}/{self.zip_name}"], check=True)
            
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
