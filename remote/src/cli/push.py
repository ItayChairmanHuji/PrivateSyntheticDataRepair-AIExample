import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent.parent.parent
    cmd = ["python", str(root / "remote/src/main.py"), "mode=push"]
    subprocess.run(cmd + sys.argv[1:])

if __name__ == "__main__":
    main()
