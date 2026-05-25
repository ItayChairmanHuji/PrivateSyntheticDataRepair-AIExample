import shutil
from pathlib import Path
import argparse

def clean_analysis_artifacts():
    """Removes generated notebooks and plots."""
    stage_root = Path(__file__).parent.parent.parent
    notebooks_dir = stage_root / "notebooks"
    
    if notebooks_dir.exists():
        for f in notebooks_dir.glob("*.ipynb"):
            print(f"Removing {f.name}")
            f.unlink()
            
    # Also clean internal plots folder in notebooks if any
    plots_dir = notebooks_dir / "plots"
    if plots_dir.exists():
        print(f"Removing {plots_dir}")
        shutil.rmtree(plots_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean analysis artifacts")
    args = parser.parse_args()
    clean_analysis_artifacts()
    print("Cleanup complete.")
