import pandas as pd
import numpy as np
from shared.entities.dataset import Dataset
from shared.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side
from shared.entities.marginal import MarginalSet
from s04_repairing.src.repair.weighted_vc_repairer import WeightedVCRepairer
from s04_repairing.src.repair.classic_vc_repairer import ClassicVCRepairer

def test_repair_works():
    print("--- Verifying Repair Flow with Symbolic Graph ---")
    
    # 1. Setup dataset with a clear FD violation
    # Row 0, 1 violate A -> B
    data = pd.DataFrame([
        {'A': 1, 'B': 10, 'target': 0}, # 0
        {'A': 1, 'B': 20, 'target': 1}, # 1
        {'A': 2, 'B': 30, 'target': 0}, # 2
        {'A': 3, 'B': 40, 'target': 1}  # 3
    ])
    
    p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
    p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
    dc = DenialConstraint([p1, p2])
    dcs = DenialConstraints([dc])
    
    dataset = Dataset("small_test", data, dcs, "target")
    
    # Initial violations
    violations_init = dataset.get_violations()
    print(f"Initial violations: {len(violations_init)}")
    assert len(violations_init) == 1 # (0, 1)
    
    # 2. Setup mock marginals for WeightedVC
    # (Just enough to not crash)
    marginals = MarginalSet([])
    
    # 3. Run WeightedVCRepairer
    print("\nRunning WeightedVCRepairer...")
    repairer = WeightedVCRepairer(alpha=0.5)
    repaired_ds = repairer.repair(dataset, marginals)
    
    # 4. Verify results
    violations_final = repaired_ds.get_violations()
    print(f"Final violations: {len(violations_final)}")
    print(f"Final dataset size: {len(repaired_ds.data)}")
    
    assert len(violations_final) == 0, "Repair failed to remove all violations"
    assert len(repaired_ds.data) == 3, f"Expected 3 rows, got {len(repaired_ds.data)}"
    
    # 5. Run ClassicVCRepairer (random edge selection)
    print("\nRunning ClassicVCRepairer...")
    classic_repairer = ClassicVCRepairer(alpha=1.0) # Always delete both? No, random side
    repaired_ds_classic = classic_repairer.repair(dataset, marginals)
    
    violations_classic = repaired_ds_classic.get_violations()
    print(f"Final violations (Classic): {len(violations_classic)}")
    assert len(violations_classic) == 0
    print("\nSUCCESS: Repair flow verified with Symbolic Conflict Graph.")

if __name__ == "__main__":
    test_repair_works()
