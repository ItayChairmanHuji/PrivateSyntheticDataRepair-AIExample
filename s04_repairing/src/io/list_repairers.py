import os
from pathlib import Path

def list_repairers():
    config_dir = Path("s04_repairing/config")
    print("Available repairers (configurations):")
    for file in config_dir.glob("*.yaml"):
        print(f" - {file.stem}")

if __name__ == "__main__":
    list_repairers()
