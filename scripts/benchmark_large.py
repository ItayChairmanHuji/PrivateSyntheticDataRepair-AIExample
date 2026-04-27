
import pandas as pd
import time
import numpy as np
from src.loading.violation_finder import ViolationFinder
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

def run_large_benchmark():
    # 1. Create 1 million rows
    # We group rows so we have a predictable number of violations
    # n=1,000,000 rows, groups of 100 with same A
    # Total violations per group: (100 * 99 / 2) = 4,950
    # Number of groups: 10,000
    # Total potential violations: 10,000 * 4,950 = 49,500,000
    
    n = 1000000
    group_size = 100
    num_groups = n // group_size
    
    print(f"Generating {n} rows...")
    data = pd.DataFrame({
        'A': np.repeat(np.arange(num_groups), group_size),
        'B': np.arange(n)
    })
    
    # DC: t1.A = t2.A & t1.B != t2.B (Functional Dependency A -> B)
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
    
    finder = ViolationFinder()
    
    print(f"Starting violation detection on 1M rows...")
    print(f"Constraint: {dc.to_string()}")
    
    # We limit to 100,000 for this benchmark to see how fast it hits the limit
    # and then we'll try WITHOUT limit but expecting it to be slower
    start_time = time.time()
    violations_limited = finder.find_violations(data, dcs, limit=100000)
    end_time = time.time()
    print(f"Time taken (limit=100k): {end_time - start_time:.4f} seconds")
    
    # Now let's try WITHOUT limit 
    # NOTE: This might consume several GBs of RAM if not careful, 
    # but 50M rows of (int, int) in a DF is about 800MB.
    print(f"Starting violation detection WITHOUT limit (Expected ~49.5M violations)...")
    start_time = time.time()
    violations = finder.find_violations(data, dcs)
    end_time = time.time()
    
    duration = end_time - start_time
    num_violations = len(violations)
    
    print(f"Time taken (no limit): {duration:.4f} seconds")
    print(f"Number of violations found: {num_violations}")

if __name__ == "__main__":
    run_large_benchmark()
