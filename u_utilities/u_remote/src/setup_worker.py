import subprocess
import logging
from pathlib import Path
from u_utilities.u_remote.src.path_resolver import RemotePathResolver

logger = logging.getLogger(__name__)

class SetupWorker:
    """
    Handles remote environment setup (venv, dependencies).
    """
    def __init__(self, remote_host: str, remote_dir: str):
        self.remote_host = remote_host
        self.remote_dir = remote_dir

    def run_setup(self):
        """
        Runs the setup commands on the remote server.
        """
        setup_script = f"""
set -e
cd {self.remote_dir}

if [ -d ".venv" ]; then
    echo "Using existing virtual environment..."
else
    echo "Creating virtual environment..."
    if command -v virtualenv >/dev/null 2>&1; then
        virtualenv .venv
    else
        python3 -m venv .venv || python3 -m venv .venv --without-pip
    fi
fi

source .venv/bin/activate

if ! command -v pip >/dev/null 2>&1; then
    echo "Pip missing, attempting manual install..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
fi

echo "Upgrading pip..."
python3 -m pip install --upgrade pip

echo "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    # Use --no-cache-dir to avoid disk space issues on some clusters
    python3 -m pip install --no-cache-dir -r requirements.txt
else
    echo "requirements.txt not found!"
    exit 1
fi
echo "Setup complete."
"""
        logger.info(f"Running setup on {self.remote_host}...")
        try:
            subprocess.run(["ssh", self.remote_host, setup_script], check=True)
            logger.info("Remote setup successful.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Remote setup failed: {e}")
            raise
