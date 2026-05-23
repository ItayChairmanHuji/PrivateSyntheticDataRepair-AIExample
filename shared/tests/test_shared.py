import pandas as pd
import pytest
from shared.entities import Dataset, DenialConstraints, DenialConstraint, Predicate, Side, Marginal
from shared.utils import ViolationFinder

def test_violation_finder_fd():
    data = pd.DataFrame({'A': [1, 1, 2], 'B': [10, 20, 30]})
    # FD: A -> B => not(t1.A = t2.A & t1.B != t2.B)
    p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
    p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
    dcs = DenialConstraints([DenialConstraint([p1, p2])])
    
    finder = ViolationFinder()
    violations = finder.find_violations(data, dcs)
    
    assert len(violations) == 1
    assert (violations.iloc[0]['idx1'] == 0 and violations.iloc[0]['idx2'] == 1)

def test_violation_finder_order():
    data = pd.DataFrame({'A': [10, 20, 5]})
    # DC: t1.A > t2.A (violates if any t1.A > t2.A)
    p1 = Predicate(Side('A', 1, False), '>', Side('A', 2, False))
    dcs = DenialConstraints([DenialConstraint([p1])])
    
    finder = ViolationFinder()
    violations = finder.find_violations(data, dcs)
    
    # Pairs: (10, 5), (20, 10), (20, 5) -> 3 violations
    assert len(violations) == 3

def test_marginal_calculation():
    data = pd.DataFrame({'A': [1, 1, 0], 'B': [0, 1, 1]})
    marginal = Marginal(attrs=('A',), values=(1,), target=0.5)
    
    freq = marginal.calculate_frequency(data)
    assert freq == 2/3
    
    dist = marginal.calculate_distance(data)
    assert abs(dist - (2/3 - 0.5)) < 1e-6

def test_dataset_violations():
    data = pd.DataFrame({'A': [1, 1], 'B': [10, 20]})
    p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
    p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
    dcs = DenialConstraints([DenialConstraint([p1, p2])])
    
    dataset = Dataset("test", data, dcs, "B")
    violations = dataset.get_violations()
    assert len(violations) == 1
