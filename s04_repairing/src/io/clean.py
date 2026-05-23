import argparse
import shutil
from pathlib import Path

def clean(experiment: str = None):
    output_dir = Path("s04_repairing/output")
    
    if experiment:
        target_dir = output_dir / experiment
        if target_dir.exists():
            print(f"Cleaning output for experiment: {experiment}...")
            shutil.rmtree(target_dir)
            print(f"Done.")
        else:
            print(f"No output found for experiment: {experiment}.")
    else:
        print("Cleaning all outputs in s04_repairing/output...")
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean output directory for Stage 04.")
    parser.add_argument("--experiment", type=str, help="Name of the experiment to clean (optional).")
    args = parser.parse_args()
    
    clean(args.experiment)
