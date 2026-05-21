import shutil
import argparse
from pathlib import Path

def clean(dataset=None):
    root = Path(__file__).resolve().parent.parent.parent.parent
    output_dir = root / "remote" / "output"
    
    if dataset:
        target = output_dir / dataset
        if target.exists():
            print(f"Cleaning {target}...")
            shutil.rmtree(target)
    else:
        print(f"Cleaning all of {output_dir}...")
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, help="Subdirectory to clean")
    args = parser.parse_args()
    clean(args.dataset)
