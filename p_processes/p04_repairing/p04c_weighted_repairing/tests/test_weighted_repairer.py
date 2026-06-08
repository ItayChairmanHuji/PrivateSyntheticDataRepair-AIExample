import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from u_utilities.u_shared import Dataset, MarginalSet, Marginal
from u_utilities.u_shared.src.violations import ViolationSet, Violation
from p_processes.p04_repairing.p04c_weighted_repairing.src.core.weighted_vc_repairer import WeightedVCRepairer
from p_processes.p04_repairing.p04c_weighted_repairing.src.core.weights.marginal_weights import MarginalWeightCalculator
from p_processes.p04_repairing.p04c_weighted_repairing.src.core.alpha.constant_alpha import ConstantAlphaCalculator

def test_weighted_repairer_basic():
    # Simple dataset where row 0 and row 1 conflict
    df = pd.DataFrame({"A": [1, 1, 2]})
    
    # Cluster 0 contains rows 0 and 1, which conflict with each other (clique)
    vs = ViolationSet(
        cluster_indices=[np.array([0, 1]), np.array([2])],
        row_to_cluster=np.array([0, 0, 1]),
        violations=[Violation(left=np.array([0]), right=np.array([0]), symmetric=True)]
    )
    
    dataset = Dataset(name="test", data=df, dcs=MagicMock(), target="A")
    dataset.get_violations = MagicMock(return_value=vs)
    
    # Marginals: target frequency of A=1 is 1.0
    marginals = MarginalSet(marginals=[
        Marginal(attrs=("A",), values=(1,), target=1.0)
    ])
    
    repairer = WeightedVCRepairer(
        weight_calculator=MarginalWeightCalculator(dataset, marginals),
        alpha_calculator=ConstantAlphaCalculator(alpha=0.5)
    )
    repaired = repairer.repair(dataset, marginals)
    
    # Repaired should have length 2 (removed row 0 or row 1)
    assert len(repaired.data) == 2
    # One row with A=1 should remain, and one row with A=2 should remain
    assert (repaired.data["A"] == 1).sum() == 1
    assert (repaired.data["A"] == 2).sum() == 1

def test_weighted_repairer_bipartite():
    # Row 0 (A=1) conflicts with Row 1 (A=2)
    df = pd.DataFrame({"A": [1, 2, 3]})
    
    vs = ViolationSet(
        cluster_indices=[np.array([0]), np.array([1]), np.array([2])],
        row_to_cluster=np.array([0, 1, 2]),
        violations=[Violation(left=np.array([0]), right=np.array([1]), symmetric=False)]
    )
    
    dataset = Dataset(name="test", data=df, dcs=MagicMock(), target="A")
    dataset.get_violations = MagicMock(return_value=vs)
    
    # Marginals: prefer keeping A=1
    marginals = MarginalSet(marginals=[
        Marginal(attrs=("A",), values=(1,), target=1.0),
        Marginal(attrs=("A",), values=(2,), target=0.0)
    ])
    
    repairer = WeightedVCRepairer(
        weight_calculator=MarginalWeightCalculator(dataset, marginals),
        alpha_calculator=ConstantAlphaCalculator(alpha=0.5)
    )
    repaired = repairer.repair(dataset, marginals)
    
    # Should remove row 1 (A=2) and keep row 0 (A=1)
    assert len(repaired.data) == 2
    assert 1 in repaired.data["A"].values
    assert 2 not in repaired.data["A"].values
    assert 3 in repaired.data["A"].values
