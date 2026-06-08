import pandas as pd

from u_utilities.u_shared import DenialConstraint, DenialConstraints, Predicate, Side, Dataset
from u_utilities.u_violation_finder import ViolationFinder as PublicViolationFinder
from u_utilities.u_violation_finder.src import ViolationFinder


def column(name: str, index: int) -> Side:
    return Side(attr=name, index=index, is_value=False)


def literal(value: str, index: int = 1) -> Side:
    return Side(attr=value, index=index, is_value=True)


def dc(*predicates: Predicate) -> DenialConstraints:
    return DenialConstraints([DenialConstraint(list(predicates))])


def edges(collection) -> set[tuple[int, int]]:
    df = collection.to_dataframe()
    return {
        tuple(sorted((int(row.idx1), int(row.idx2))))
        for row in df.itertuples()
    }


def test_public_import_exposes_facade():
    assert PublicViolationFinder is ViolationFinder


def test_finds_partitioned_binary_violation():
    data = pd.DataFrame({"A": [1, 1, 2], "B": ["x", "y", "x"]})
    constraints = dc(
        Predicate(column("A", 1), "=", column("A", 2)),
        Predicate(column("B", 1), "!=", column("B", 2)),
    )
    ds = Dataset("test", data, constraints, "B")
    violations = ViolationFinder().find_violations(ds)

    assert edges(violations) == {(0, 1)}


def test_finds_internal_group_violation():
    data = pd.DataFrame({"A": [1, 1, 2]})
    constraints = dc(Predicate(column("A", 1), "=", column("A", 2)))
    ds = Dataset("test", data, constraints, "A")
    violations = ViolationFinder().find_violations(ds)

    assert edges(violations) == {(0, 1)}


def test_counts_internal_group_edges_once():
    data = pd.DataFrame({"A": [1, 1, 1]})
    constraints = dc(Predicate(column("A", 1), "=", column("A", 2)))
    ds = Dataset("test", data, constraints, "A")
    violations = ViolationFinder().find_violations(ds)

    assert len(violations) == 3
    assert len(violations.to_dataframe()) == 3


def test_partitions_nullable_equality_keys():
    data = pd.DataFrame({"A": [None, None, 1], "B": ["x", "y", "x"]})
    constraints = dc(
        Predicate(column("A", 1), "=", column("A", 2)),
        Predicate(column("B", 1), "!=", column("B", 2)),
    )
    ds = Dataset("test", data, constraints, "B")
    violations = ViolationFinder().find_violations(ds)

    assert edges(violations) == {(0, 1)}


def test_finds_unary_literal_violation():
    data = pd.DataFrame({"age": [25, 10, 30]})
    constraints = dc(
        Predicate(column("age", 1), ">", literal("20")),
        Predicate(column("age", 2), "<", literal("20", index=2)),
    )
    ds = Dataset("test", data, constraints, "age")
    violations = ViolationFinder().find_violations(ds)

    assert edges(violations) == {(0, 1), (1, 2)}


def test_compares_numeric_literals_against_string_columns():
    data = pd.DataFrame({"age": ["25", "10", "30"]})
    constraints = dc(
        Predicate(column("age", 1), ">", literal("20")),
        Predicate(column("age", 2), "<", literal("20", index=2)),
    )
    ds = Dataset("test", data, constraints, "age")
    violations = ViolationFinder().find_violations(ds)

    assert edges(violations) == {(0, 1), (1, 2)}


def test_respects_reversed_tuple_sides():
    data = pd.DataFrame({"low": [1, 3], "high": [2, 4]})
    constraints = dc(Predicate(column("high", 2), ">", column("low", 1)))
    ds = Dataset("test", data, constraints, "high")
    violations = ViolationFinder().find_violations(ds)

    assert edges(violations) == {(0, 1)}
