import pandas as pd
from pandas import DataFrame

from denial_constraints.violation_finding.sql_executor import execute_sql
from denial_constraints.entities.workload import Workload
from denial_constraints.violation_finding.workload_builder import build_workload


def find_violations(data: DataFrame, dcs) -> DataFrame:
    data = _preprocess_data(data, dcs)
    workloads = _workloads(data, dcs)
    violations = _execute_workloads(workloads)
    if not violations:
        return pd.DataFrame(columns=["id1", "id2"])
    return pd.concat(violations, ignore_index=True)


def _preprocess_data(data: DataFrame, dcs) -> DataFrame:
    scoped = data.drop(columns=[col for col in data.columns if col not in dcs.attrs])
    data_with_idx = scoped.copy(deep=False)
    data_with_idx["idx"] = range(1, len(data_with_idx) + 1)
    return data_with_idx


def _workloads(data_with_idx: DataFrame, dcs) -> list[Workload]:
    workloads = [
        build_workload(data_with_idx, constraint) for constraint in dcs.constraints
    ]
    return [workload for workload in workloads if workload is not None]


def _execute_workloads(workloads: list[Workload]) -> list[DataFrame]:
    return [execute_sql(workload) for workload in workloads]
