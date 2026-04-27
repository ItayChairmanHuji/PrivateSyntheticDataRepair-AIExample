from pandas import DataFrame

from denial_constraints.entities.denial_constraint import DenialConstraint
from denial_constraints.violation_finding.query_builder import build_constraint_query
from denial_constraints.entities.workload import Workload
from denial_constraints.violation_finding.filters import unary_filter, fds_filter, monotonic_filter


def build_workload(data: DataFrame, constraint: DenialConstraint) -> Workload | None:
    workload = Workload(data, data, "")
    workload = _apply_filters(workload, constraint)
    if workload is None:
        return None
    workload.query = build_constraint_query(constraint)
    return workload


def _has_empty_side(sides: tuple[DataFrame, DataFrame]) -> bool:
    return any(side.empty for side in sides)


def _apply_filters(workload: Workload, constraint: DenialConstraint) -> Workload | None:
    filters = [
        unary_filter.filter_workload,
        fds_filter.filter_workload,
        monotonic_filter.filter_workload,
    ]
    for f in filters:
        workload = f(workload, constraint)
        if _has_empty_side((workload.first, workload.second)):
            return None
    return workload
