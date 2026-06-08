import pandas as pd

from u_utilities.u_shared import Dataset, DenialConstraints, Predicate, Side
from u_utilities.u_violation_finder import ViolationFinder


def column(name, index):
    return Side(attr=name, index=index, is_value=False)


def dc(*predicates):
    from u_utilities.u_shared import DenialConstraint

    return DenialConstraints(constraints=[DenialConstraint(predicates=list(predicates))])


def test_dataset_integration():
    data = pd.DataFrame({"A": [1, 1, 2], "B": ["x", "y", "x"]})
    constraints = dc(
        Predicate(column("A", 1), "=", column("A", 2)),
        Predicate(column("B", 1), "!=", column("B", 2)),
    )

    dataset = Dataset(name="test", data=data, dcs=constraints, target="B")

    # 1. Test manual compaction
    compact = dataset.compact()
    assert len(compact.df) == 3  # All rows are unique in {A, B}

    # 2. Test auto-compaction in finder
    finder = ViolationFinder()
    violations = finder.find_violations(dataset)

    # Rows 0 and 1 violate: A=1, B='x' != B='y'
    # The current scanner implementation might add both orientations
    assert len(violations.to_dataframe()) == 1

    # 3. Test caching
    compact2 = dataset.compact()
    assert compact is compact2


def test_dataset_internal_violation():
    # Duplicate rows in A
    data = pd.DataFrame({"A": [1, 1, 2]})
    constraints = dc(Predicate(column("A", 1), "=", column("A", 2)))

    dataset = Dataset(name="test", data=data, dcs=constraints, target="A")

    # Compacting by A
    compact = dataset.compact()
    assert len(compact.df) == 2  # Values are {1, 2}

    violations = ViolationFinder().find_violations(dataset)
    # Cluster for A=1 has 2 rows, it conflicts with itself
    assert len(violations.to_dataframe()) == 1
