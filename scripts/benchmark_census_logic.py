
import time
import pandas as pd
import numpy as np
from src.loading.violation_finder import ViolationFinder
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

def benchmark_conditional_fd():
    # Simulate census-like data: 1M rows
    # A = 0 (30% of data), A = 1 (70% of data)
    # Among A=0, we have an FD: B -> C
    # B has 10 values. C has 2 values.
    
    n = 1000000
    A = np.random.choice([0, 1], size=n, p=[0.3, 0.7])
    B = np.random.randint(0, 10, size=n)
    C = np.random.randint(0, 2, size=n)
    
    data = pd.DataFrame({'AGEP': A, 'CIT': B, 'NATIVITY': C})
    
    # DC: not(t1.AGEP=0 & t2.AGEP=0 & t1.CIT=t2.CIT & t1.NATIVITY!=t2.NATIVITY)
    preds = [
        Predicate(Side('AGEP', 1, False), '=', Side('0', 1, True)),
        Predicate(Side('AGEP', 2, False), '=', Side('0', 2, True)),
        Predicate(Side('CIT', 1, False), '=', Side('CIT', 2, False)),
        Predicate(Side('NATIVITY', 1, False), '!=', Side('NATIVITY', 2, False))
    ]
    dc = DenialConstraint(preds)
    dcs = DenialConstraints([dc])
    
    finder = ViolationFinder()
    
    print(f"Benchmark: {dc.to_string()}")
    start = time.time()
    v = finder.find_violations(data, dcs, limit=100000)
    end = time.time()
    print(f"Time (limit 100k): {end - start:.4f}s")
    print(f"Found {len(v)} violations.")

    start = time.time()
    v = finder.find_violations(data, dcs)
    end = time.time()
    print(f"Time (no limit): {end - start:.4f}s")
    print(f"Found {len(v)} violations.")

if __name__ == "__main__":
    benchmark_conditional_fd()
