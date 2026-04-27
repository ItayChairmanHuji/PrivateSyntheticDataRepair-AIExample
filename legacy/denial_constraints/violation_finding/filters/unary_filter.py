import pandas as pd
from pandas import DataFrame

from denial_constraints.entities.denial_constraint import DenialConstraint
from denial_constraints.entities.workload import Workload


def filter_workload(workload: Workload, dc: DenialConstraint):
    func = lambda data, side: _filter_side(data, dc, side)
    return workload.run_both(func)


def _filter_side(data: DataFrame, dc: DenialConstraint, side: int) -> DataFrame:
    predicates = dc.predicates_for_tuple(side)
    if not predicates:
        return data
    mask = _predicate_mask(data, predicates)
    return data.loc[mask]


def _predicate_mask(data: DataFrame, tuple_predicates: list) -> pd.Series:
    mask = pd.Series(True, index=data.index)
    for predicate in tuple_predicates:
        mask &= predicate.eval(data)
        if not mask.any():
            return mask
    return mask
