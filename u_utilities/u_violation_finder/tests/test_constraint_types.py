import pandas as pd
import numpy as np
import pytest
from u_utilities.u_shared import Dataset, DenialConstraint, DenialConstraints, Predicate, Side
from u_utilities.u_violation_finder import ViolationFinder

def col(name: str, index: int) -> Side:
    return Side(attr=name, index=index, is_value=False)

def val(value, index: int = 1) -> Side:
    return Side(attr=value, index=index, is_value=True)

def dc_list(*predicates: Predicate) -> DenialConstraints:
    return DenialConstraints([DenialConstraint(list(predicates))])

def get_edges(violations) -> set[tuple[int, int]]:
    df = violations.to_dataframe()
    if df.empty:
        return set()
    return {
        tuple(sorted((int(row.idx1), int(row.idx2))))
        for row in df.itertuples()
    }

@pytest.fixture
def finder():
    return ViolationFinder()

def test_fd_engine(finder):
    # FD: A=A & B!=B
    data = pd.DataFrame({
        "A": [1, 1, 2, 2],
        "B": ["x", "y", "x", "x"]
    })
    constraints = dc_list(
        Predicate(col("A", 1), "=", col("A", 2)),
        Predicate(col("B", 1), "!=", col("B", 2))
    )
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    # Only (0, 1) violates because they have same A but different B
    assert get_edges(violations) == {(0, 1)}

def test_conditional_constant_engine(finder):
    # CC: A=A & B!=B & t1.C='v1'
    data = pd.DataFrame({
        "A": [1, 1, 1],
        "B": ["x", "y", "x"],
        "C": ["v1", "v2", "v1"]
    })
    # If we say t1.C='v1', then only t1=0 or t1=2 can be in the violation
    # If t1=0, t2=1 violates (A=1, B='x'!='y')
    # If t1=2, t2=1 violates (A=1, B='x'!='y')
    constraints = dc_list(
        Predicate(col("A", 1), "=", col("A", 2)),
        Predicate(col("B", 1), "!=", col("B", 2)),
        Predicate(col("C", 1), "=", val("v1"))
    )
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    assert get_edges(violations) == {(0, 1), (1, 2)}

def test_single_order_engine(finder):
    # Order: A > A
    data = pd.DataFrame({
        "A": [10, 20, 30]
    })
    constraints = dc_list(
        Predicate(col("A", 1), ">", col("A", 2))
    )
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    # (1, 0): 20 > 10
    # (2, 0): 30 > 10
    # (2, 1): 30 > 20
    assert get_edges(violations) == {(0, 1), (0, 2), (1, 2)}

def test_two_order_engine(finder):
    # Two Order: A > A & B < B
    data = pd.DataFrame({
        "A": [10, 20, 15],
        "B": [100, 50, 150]
    })
    constraints = dc_list(
        Predicate(col("A", 1), ">", col("A", 2)),
        Predicate(col("B", 1), "<", col("B", 2))
    )
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    
    # Check pairs:
    # (1, 0): 20 > 10 AND 50 < 100 -> YES
    # (2, 0): 15 > 10 AND 150 < 100 -> NO
    # (1, 2): 20 > 15 AND 50 < 150 -> YES
    assert get_edges(violations) == {(0, 1), (1, 2)}

def test_duckdb_engine_fallback(finder):
    # General: A=A & B > B
    data = pd.DataFrame({
        "A": [1, 1, 2],
        "B": [10, 5, 20]
    })
    constraints = dc_list(
        Predicate(col("A", 1), "=", col("A", 2)),
        Predicate(col("B", 1), ">", col("B", 2))
    )
    # This should be routed to DuckDB because OrderEngine only handles pure order
    # and FDEngine only handles equality + 1 inequality.
    # Wait, actually analyzer.py says:
    # if not order_preds and len(neq_attrs) == 1: ...
    # Here order_preds=1 (B > B), eq_attrs=1 (A=A). 
    # It will fall through to GENERAL.
    
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    
    # (0, 1): A=1, 10 > 5 -> YES
    assert get_edges(violations) == {(0, 1)}

def test_fd_with_nulls(finder):
    data = pd.DataFrame({
        "A": [1, 1, None, None],
        "B": ["x", "y", "x", "y"]
    })
    constraints = dc_list(
        Predicate(col("A", 1), "=", col("A", 2)),
        Predicate(col("B", 1), "!=", col("B", 2))
    )
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    # A=1 group: (0, 1) violates
    # A=None group: (2, 3) violates (if NULL IS NOT DISTINCT FROM NULL)
    # In FDEngine, groupby(dropna=False) is used, so it should find both.
    assert get_edges(violations) == {(0, 1), (2, 3)}

def test_order_with_nulls(finder):
    data = pd.DataFrame({
        "A": [10, None, 20]
    })
    constraints = dc_list(
        Predicate(col("A", 1), ">", col("A", 2))
    )
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    # (2, 0) violates: 20 > 10
    # None should not violate anything in order comparison
    assert get_edges(violations) == {(0, 2)}

def test_multiple_dcs(finder):
    data = pd.DataFrame({
        "A": [1, 1, 2],
        "B": ["x", "y", "x"],
        "C": [10, 20, 30]
    })
    # DC1: A=A & B!=B (FD) -> (0, 1)
    # DC2: C > C (Order) -> (1, 0), (2, 0), (2, 1)
    constraints = DenialConstraints([
        DenialConstraint([
            Predicate(col("A", 1), "=", col("A", 2)),
            Predicate(col("B", 1), "!=", col("B", 2))
        ]),
        DenialConstraint([
            Predicate(col("C", 1), ">", col("C", 2))
        ])
    ])
    ds = Dataset("test", data, constraints, target="B")
    violations = finder.find_violations(ds)
    
    assert get_edges(violations) == {(0, 1), (0, 2), (1, 2)}
