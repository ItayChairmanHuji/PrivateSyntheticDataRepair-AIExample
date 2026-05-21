import shutil
from pathlib import Path
import os
import argparse

def clean(dataset_name=None):
    output_dir = Path("s01_loading/output")
    if dataset_name:
        target_dir = output_dir / dataset_name
        if target_dir.exists():
            print(f"Cleaning {target_dir}...")
            shutil.rmtree(target_dir)
            print("Done.")
        else:
            print(f"Directory {target_dir} does not exist. Nothing to clean.")
    else:
        if output_dir.exists():
            print(f"Cleaning all outputs in {output_dir}...")
            for item in output_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print("Done.")
        else:
            print(f"Directory {output_dir} does not exist. Nothing to clean.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean Stage 1 outputs.")
    parser.add_argument("--dataset", type=str, help="Specific dataset subdirectory to clean.")
    args = parser.parse_args()
    clean(args.dataset)
