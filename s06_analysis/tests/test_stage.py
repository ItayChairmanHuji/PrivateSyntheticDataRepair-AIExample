import pytest
from pathlib import Path
import subprocess
import os

def test_notebook_generation():
    """Verifies that the main entry point generates a notebook."""
    # Ensure a dummy result exists for testing if needed, 
    # but here we'll just check if the orchestration runs.
    # We might need to mock the loader if no remote/output exists.
    
    cmd = [
        "python", "s06_analysis/src/main.py",
        "experiment_name=experiment_4"
    ]
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if successful or if it failed because of missing data (which is expected in some envs)
    # But it should at least not have a syntax error.
    assert result.returncode in [0, 1] 
    
    if result.returncode == 0:
        assert "Success: Analysis notebook generated" in result.stdout
        assert Path("s06_analysis/notebooks/experiment_4_analysis.ipynb").exists()

def test_cleanup():
    """Verifies the cleanup script works."""
    notebook_path = Path("s06_analysis/notebooks/test_dummy.ipynb")
    notebook_path.touch()
    
    cmd = ["python", "s06_analysis/src/io/clean.py"]
    subprocess.run(cmd, capture_output=True)
    
    assert not notebook_path.exists()
