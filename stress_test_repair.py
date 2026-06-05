import pandas as pd
import numpy as np
import time
from shared.entities.dataset import Dataset
from shared.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side
from shared.entities.marginal import MarginalSet
from s04_repairing.src.repair.weighted_vc_repairer import WeightedVCRepairer

def test_large_repair():
    print("--- Stress Testing Repairer with Symbolic Graph (1000 rows) ---")
    
    # 1. Create a dataset with 1000 rows and many violations
    # Use 10 unique values for A, each appearing 100 times.
    # DC: A -> B where B is random.
    np.random.seed(42)
    n = 1000
    a_vals = np.repeat(np.arange(10), 100)
    b_vals = np.random.randint(0, 1000, n)
    data = pd.DataFrame({'A': a_vals, 'B': b_vals, 'target': 0})
    
    p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
    p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
    dc = DenialConstraint([p1, p2])
    dcs = DenialConstraints([dc])
    
    dataset = Dataset("stress_test", data, dcs, "target")
    
    # 2. Run Repair
    print(f"Initial violations: {len(dataset.get_violations())}")
    
    repairer = WeightedVCRepairer(alpha=0.5)
    marginals = MarginalSet([])
    
    start_time = time.time()
    repaired_ds = repairer.repair(dataset, marginals)
    end_time = time.time()
    
    # 3. Verify
    violations_final = repaired_ds.get_violations()
    print(f"Final violations: {len(violations_final)}")
    print(f"Final dataset size: {len(repaired_ds.data)}")
    print(f"Time taken for 1000 rows: {end_time - start_time:.2f}s")
    
    assert len(violations_final) == 0
    # For A->B, we should keep 1 row per unique A
    # Since there are 10 unique A values, we expect 10 rows.
    assert len(repaired_ds.data) == 10
    print("SUCCESS: Large repair verified.")

if __name__ == "__main__":
    test_large_repair()
