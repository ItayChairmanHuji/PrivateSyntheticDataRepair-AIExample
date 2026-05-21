import argparse
import shutil
from pathlib import Path

def clean(dataset: str = None):
    output_dir = Path("s05_evaluating/output")
    
    if dataset:
        target_dir = output_dir / dataset
        if target_dir.exists():
            print(f"Cleaning output for dataset: {dataset}...")
            shutil.rmtree(target_dir)
            print(f"Done.")
        else:
            print(f"No output found for dataset: {dataset}.")
    else:
        print("Cleaning all outputs in s05_evaluating/output...")
        if output_dir.exists():
            for item in output_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        print("Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean output directory for Stage 05.")
    parser.add_argument("--dataset", type=str, help="Name of the dataset to clean (optional).")
    args = parser.parse_args()
    
    clean(args.dataset)
