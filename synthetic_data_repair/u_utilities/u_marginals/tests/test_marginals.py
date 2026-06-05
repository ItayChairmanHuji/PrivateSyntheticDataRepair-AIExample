import pytest
import pandas as pd
import numpy as np
from u_utilities.u_shared import Dataset, DenialConstraints
from u_utilities.u_marginals import (
    MarginalManager, MarginalCalculator, MarginalError, 
    SelectionMethod, ErrorMetric
)

@pytest.fixture
def mock_datasets():
    data_p = pd.DataFrame({
        "age": [20, 30, 40, 20],
        "sex": ["M", "F", "M", "F"],
        "income": [0, 1, 1, 0]
    })
    data_s = pd.DataFrame({
        "age": [20, 20, 40, 40],
        "sex": ["M", "M", "F", "F"],
        "income": [1, 1, 0, 0]
    })
    dcs = DenialConstraints(constraints=[])
    
    p_ds = Dataset(name="test", data=data_p, dcs=dcs, target="income")
    s_ds = Dataset(name="test", data=data_s, dcs=dcs, target="income")
    return p_ds, s_ds

def test_marginal_calculator(mock_datasets):
    p_ds, _ = mock_datasets
    calc = MarginalCalculator()
    freqs = calc.compute_frequencies(p_ds.data, ("age", "sex"))
    assert freqs[(20, "M")] == 0.25
    assert freqs[(30, "F")] == 0.25

def test_marginal_error():
    err = MarginalError()
    p_vals = np.array([0.5, 0.1])
    s_vals = np.array([0.4, 0.2])
    res = err.compute(p_vals, s_vals, metric=ErrorMetric.ABS)
    assert np.allclose(res, [0.1, 0.1])

def test_marginal_manager_obtain(mock_datasets):
    p_ds, s_ds = mock_datasets
    manager = MarginalManager()
    
    # Test Top-K selection
    m_set = manager.obtain(p_ds, s_ds, k=2, selection_budget=100.0, generation_budget=100.0)
    
    assert len(m_set.marginals) <= 2
    for m in m_set.marginals:
        assert len(m.attrs) == 2
        assert m.target >= 0.0 and m.target <= 1.0

def test_marginal_manager_invalid_method(mock_datasets):
    p_ds, s_ds = mock_datasets
    manager = MarginalManager()
    with pytest.raises(ValueError, match="is not a valid SelectionMethod"):
        manager.obtain(p_ds, s_ds, method="invalid")
