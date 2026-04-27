
import pandas as pd
import time
from src.loading.violation_finder import ViolationFinder
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

def run_benchmark():
    # 1. Create synthetic data
    # 1000 rows with same 'A', different 'B' -> (1000 * 999 / 2) = 499,500 violations
    n = 1000
    data = pd.DataFrame({
        'A': [1] * n,
        'B': list(range(n))
    })
    
    # 2. Define DC: t1.A = t2.A & t1.B != t2.B
    pred1 = Predicate(
        left=Side(attr='A', index=1, is_value=False),
        opr='=',
        right=Side(attr='A', index=2, is_value=False)
    )
    pred2 = Predicate(
        left=Side(attr='B', index=1, is_value=False),
        opr='!=',
        right=Side(attr='B', index=2, is_value=False)
    )
    dc = DenialConstraint(predicates=[pred1, pred2])
    dcs = DenialConstraints(constraints=[dc])
    
    print(f"Running benchmark with {n} rows and 1 DC.")
    print(f"Constraint: {dc.to_string()}")
    
    finder = ViolationFinder()
    
    # Measure time
    start_time = time.time()
    violations = finder.find_violations(data, dcs)
    end_time = time.time()
    
    duration = end_time - start_time
    num_violations = len(violations)
    
    print(f"Time taken: {duration:.4f} seconds")
    print(f"Number of violations found: {num_violations}")
    
    if num_violations == (n * (n - 1) / 2):
        print("Success: Found all expected violations.")
    else:
        print(f"Warning: Expected {int(n * (n - 1) / 2)} violations, but found {num_violations}.")

    # Let's try a larger scale: 2000 rows -> ~2,000,000 violations
    n2 = 2000
    data2 = pd.DataFrame({
        'A': [1] * n2,
        'B': list(range(n2))
    })
    
    print(f"\nRunning benchmark with {n2} rows.")
    start_time = time.time()
    violations2 = finder.find_violations(data2, dcs)
    end_time = time.time()
    
    duration2 = end_time - start_time
    num_violations2 = len(violations2)
    
    print(f"Time taken: {duration2:.4f} seconds")
    print(f"Number of violations found: {num_violations2}")

    # Scale to 5000 rows -> ~12.5M violations
    n3 = 5000
    data3 = pd.DataFrame({
        'A': [1] * n3,
        'B': list(range(n3))
    })
    
    print(f"\nRunning benchmark with {n3} rows.")
    start_time = time.time()
    violations3 = finder.find_violations(data3, dcs)
    end_time = time.time()
    
    duration3 = end_time - start_time
    num_violations3 = len(violations3)
    
    print(f"Time taken: {duration3:.4f} seconds")
    print(f"Number of violations found: {num_violations3}")

if __name__ == "__main__":
    run_benchmark()
