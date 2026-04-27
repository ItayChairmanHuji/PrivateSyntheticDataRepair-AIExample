from collections import namedtuple

import pandas as pd
from pandas import DataFrame

from denial_constraints.entities.denial_constraint import DenialConstraint
from denial_constraints.entities.predicate import Predicate
from denial_constraints.entities.workload import Workload

IndexGroup = namedtuple("IndexGroup", ["keys", "data"])


def filter_workload(workload: Workload, dc: DenialConstraint) -> Workload:
    if not _should_filter(dc):
        return workload

    g1, g2 = workload.run_both(lambda x, y: _get_group_index(x, dc, y), keep_type=False)
    merged = pd.merge(g1.data, g2.data, left_on=g1.keys, right_on=g2.keys, suffixes=('_1', '_2'))
    suspect_keys = _get_suspect_keys(merged)
    keys = [g1.keys, g2.keys]
    return workload.run_both(lambda x, y: _prune(x, suspect_keys, keys[y]))


def _should_filter(dc: DenialConstraint) -> bool:
    preds = dc.cross_predicates
    equality = len([p for p in preds if p.opr == "="])
    not_equal = len([p for p in preds if p.opr == "!="])
    return equality == len(preds) - 1 and not_equal == 1


def _get_group_index(data: DataFrame, dc: DenialConstraint, index: int):
    tuple_id = index + 1
    equality_preds = [p for p in dc.cross_predicates if p.opr == "="]
    inequality_pred = [p for p in dc.cross_predicates if p.opr == "!="][0]
    keys = _attrs(equality_preds, tuple_id)
    vals = _attrs([inequality_pred], tuple_id)[0]
    group = _get_group_stats(data, keys, vals)
    return IndexGroup(keys=keys, data=group)


def _get_group_stats(data: DataFrame, keys: list[str], val: str) -> DataFrame:
    return data.groupby(keys, dropna=False)[val].agg(nunique="nunique", min="min").reset_index()


def _attrs(preds: list[Predicate], index: int) -> list[str]:
    attrs = []
    for p in preds:
        if p.left.index == index:
            attrs.append(p.left.attr)
        elif p.right.index == index:
            attrs.append(p.right.attr)
    return attrs


def _get_suspect_keys(merged: DataFrame) -> DataFrame:
    is_safe = (
            (merged["nunique_1"] == 1) &
            (merged["nunique_2"] == 1) &
            (merged["min_1"] == merged["min_2"])
    )
    return merged.loc[~is_safe]


def _prune(data: DataFrame, suspects, keys: list[str]) -> DataFrame:
    return data.merge(suspects[keys].drop_duplicates(), on=keys, how="inner") if not suspects.empty else data.iloc[0:0]
