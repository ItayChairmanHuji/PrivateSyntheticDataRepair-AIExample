import pandas as pd
import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.loading.violation_finder import ViolationFinder
from src.loading.components.dcs_loader import DCsLoader
from pathlib import Path

def check():
    finder = ViolationFinder()
    loader = DCsLoader()
    df = pd.DataFrame({'A': [1, 1, 2], 'B': [10, 20, 10]})
    
    path = Path("tmp_dcs.txt")
    path.write_text("not(t1.A=1 & t1.B>15)")
    dcs = loader.load(path)
    
    violations = finder.find_violations(df, dcs)
    print("Violations:")
    print(violations)
    
    if path.exists():
        path.unlink()

if __name__ == "__main__":
    check()
