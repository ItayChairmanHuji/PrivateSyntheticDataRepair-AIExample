from collections import namedtuple

from pandas import DataFrame

from denial_constraints.entities.denial_constraint import DenialConstraint
from denial_constraints.entities.predicate import Predicate
from denial_constraints.entities.workload import Workload

IndexGroup = namedtuple("IndexGroup", ["keys", "data"])


def filter_workload(workload: Workload, dc: DenialConstraint) -> Workload:
    if not _should_monotonic_filter(dc):
        return workload

    ineq_preds = [p for p in dc.cross_predicates if p.opr in {"<", "<=", ">", ">="}]
    eq_preds = [p for p in dc.cross_predicates if p.opr == "="]

    if not eq_preds:
        return workload

    attr_a = _attrs([ineq_preds[0]], 1)[0]
    attr_b = _attrs([ineq_preds[1]], 1)[0]
    group_keys = _attrs(eq_preds, 1)
    suspect_keys = _find_inversion_groups(workload.first, group_keys, attr_a, attr_b)
    keys_list = [group_keys, group_keys]
    return workload.run_both(lambda data, idx: _prune(data, suspect_keys, keys_list[idx]))


def _should_monotonic_filter(dc: DenialConstraint) -> bool:
    cross = dc.cross_predicates
    ineqs = [p for p in cross if p.opr in {"<", "<=", ">", ">="}]
    return len(ineqs) == 2 and not dc.unary_predicates


def _find_inversion_groups(data: DataFrame, group_keys: list[str], col_a: str, col_b: str) -> DataFrame:
    if data.empty:
        return DataFrame(columns=group_keys)

    df = data.sort_values(group_keys + [col_a])
    group_obj = df.groupby(group_keys, dropna=False)[col_b]
    is_inversion = (df[col_b] < group_obj.cummax().shift(1))
    bad_group_keys = df.loc[is_inversion, group_keys].drop_duplicates()
    return bad_group_keys


def _prune(data: DataFrame, suspect_keys: DataFrame, keys: list[str]) -> DataFrame:
    return data.merge(suspect_keys, on=keys, how="inner") if not suspect_keys.empty else data.iloc[0:0]


def _attrs(preds: list[Predicate], tuple_id: int) -> list[str]:
    attrs = []
    for p in preds:
        if p.left.index == tuple_id:
            attrs.append(p.left.attr)
        elif p.right.index == tuple_id:
            attrs.append(p.right.attr)
    return attrs