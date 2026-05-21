import subprocess
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--blueprint", type=str, required=True)
    args, unknown = parser.parse_known_args()
    
    root = Path(__file__).resolve().parent.parent.parent.parent
    cmd = ["python", str(root / "remote/src/main.py"), "mode=pull", f"blueprint={args.blueprint}"]
    subprocess.run(cmd + unknown)

if __name__ == "__main__":
    main()
