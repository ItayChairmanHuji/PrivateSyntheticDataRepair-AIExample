import pandas as pd
import numpy as np
import pytest
from unittest.mock import MagicMock
from u_utilities.u_shared import Dataset, MarginalSet, Marginal
from u_utilities.u_shared.src.violations import ViolationSet, Violation

try:
    import gurobipy as gp
    from p_processes.p04_repairing.p04d_ilp_repairing.src.core.ilp_repairer import ILPRepairer
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False

@pytest.mark.skipif(not GUROBI_AVAILABLE, reason="Gurobi not installed")
def test_ilp_repairer_basic():
    # Simple dataset where row 0 and row 1 conflict
    df = pd.DataFrame({"A": [1, 1, 2]})
    
    vs = ViolationSet(
        cluster_indices=[np.array([0, 1]), np.array([2])],
        row_to_cluster=np.array([0, 0, 1]),
        violations=[Violation(left=np.array([0]), right=np.array([0]), symmetric=True)]
    )
    
    dataset = Dataset(name="test", data=df, dcs=MagicMock(), target="A")
    dataset.get_violations = MagicMock(return_value=vs)
    
    repairer = ILPRepairer(alpha=0.5, use_marginals=False)
    
    try:
        repaired = repairer.repair(dataset, None)
        assert len(repaired.data) == 2
    except Exception as e:
        if "No Gurobi license" in str(e) or "Model too large" in str(e):
             pytest.skip(f"Gurobi license issue: {e}")
        raise e
