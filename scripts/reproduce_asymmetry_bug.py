import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.loading.violation_finder import ViolationFinder
from src.loading.components.dcs_loader import DCsLoader
from pathlib import Path

def reproduce():
    finder = ViolationFinder()
    loader = DCsLoader()
    
    # Dataset with Row 0: A=2, Row 1: A=1
    df = pd.DataFrame({'A': [2, 1]})
    
    # DC: not(t1.A=1 & t2.A=2)
    # This is ASYMMETRIC. 
    # Tuple 1 must be Row 1 (A=1)
    # Tuple 2 must be Row 0 (A=2)
    # The pair is (1, 0), which should be normalized to (0, 1) in the output.
    
    dcs_path = Path("reproduce_dcs.txt")
    dcs_path.write_text("not(t1.A=1 & t2.A=2)")
    dcs = loader.load(dcs_path)
    
    print(f"Testing DC: {dcs.constraints[0].to_string()}")
    violations = finder.find_violations(df, dcs)
    
    print(f"Violations found: {violations.to_dict('records')}")
    
    expected = [{'idx1': 0, 'idx2': 1}]
    actual = violations.to_dict('records')
    
    if actual == expected:
        print("SUCCESS: Asymmetric violation found and normalized.")
    elif len(actual) == 0:
        print("FAILURE: Asymmetric violation MISSED!")
    else:
        print(f"FAILURE: Unexpected output: {actual}")

    # Cleanup
    if dcs_path.exists():
        dcs_path.unlink()

if __name__ == "__main__":
    reproduce()
