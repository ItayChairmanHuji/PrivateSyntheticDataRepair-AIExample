import os
import zipfile
import subprocess
from pathlib import Path

# Configuration
REMOTE_HOST = "snorlax-login"
REMOTE_DIR = "~/final_research"
ZIP_NAME = "code_sync.zip"
EXCLUDES = {
    ".git", ".venv", "__pycache__", "data", "outputs", "old", "models", 
    ".vscode", ZIP_NAME, "s06_remote/output"
}

def create_zip(zip_path, root_dir):
    print(f"Creating zip archive: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in EXCLUDES and not d.startswith('.')]
            
            for file in files:
                if file in EXCLUDES or file.startswith('.'):
                    continue
                
                file_path = Path(root) / file
                arcname = file_path.relative_to(root_dir)
                
                # Check if any parent directory is in EXCLUDES
                if any(part in EXCLUDES for part in arcname.parts):
                    continue
                
                # Read content and ensure Unix line endings for scripts
                if file.endswith('.sh') or file.endswith('.py'):
                    with open(file_path, 'rb') as f:
                        content = f.read().replace(b'\r\n', b'\n')
                    zipf.writestr(str(arcname), content)
                else:
                    zipf.write(file_path, arcname)
    print("Zip archive created.")

def upload_and_extract():
    root_dir = Path(__file__).parent.parent.parent
    zip_path = root_dir / ZIP_NAME
    
    # 1. Create Zip
    create_zip(zip_path, root_dir)
    
    try:
        # 2. Upload to remote
        print(f"Uploading {ZIP_NAME} to {REMOTE_HOST}:{REMOTE_DIR}")
        subprocess.run(["scp", str(zip_path), f"{REMOTE_HOST}:{REMOTE_DIR}/{ZIP_NAME}"], check=True)
        
        # 3. Extract on remote
        print("Extracting on remote...")
        extract_cmd = f"cd {REMOTE_DIR} && unzip -o {ZIP_NAME} && rm {ZIP_NAME}"
        subprocess.run(["ssh", REMOTE_HOST, extract_cmd], check=True)
        
        print("Successfully uploaded and extracted code to remote.")
    finally:
        # 4. Cleanup local zip
        if zip_path.exists():
            os.remove(zip_path)
            print("Cleaned up local zip archive.")

if __name__ == "__main__":
    upload_and_extract()
