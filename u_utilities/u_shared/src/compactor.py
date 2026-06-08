import numpy as np
import pandas as pd
from pandas import Series

from .compact_data import CompactData


def compact_data(data: pd.DataFrame, attributes: list[str]) -> CompactData:
    return _compact_non_empty(data, attributes) if len(data) > 0 else _empty(attributes)

def _empty(attributes: list[str]):
    return CompactData(
        df=pd.DataFrame(columns=Series(attributes)),
        _compact_to_dense=[],
        _dense_to_compact=np.array([], dtype=int),
        attributes=attributes,
    )

def _compact_non_empty(data: pd.DataFrame, attributes: list[str]):
    dense_size = len(data)
    grouped = data.groupby(attributes, dropna=False).indices
    compact_to_dense, dense_to_compact = _create_mappings(grouped, dense_size)
    df = _create_df(data, compact_to_dense, attributes)
    return CompactData(
        df=df,
        _compact_to_dense=compact_to_dense,
        _dense_to_compact=dense_to_compact,
        attributes=attributes
    )

def _create_mappings(grouped, dense_size):
    compact_to_dense = [np.asarray(indices, dtype=int) for indices in grouped.values()]
    dense_to_compact = np.zeros(dense_size, dtype=int)
    for cluster_id, indices in enumerate(compact_to_dense):
        dense_to_compact[indices] = cluster_id
    return compact_to_dense, dense_to_compact

def _create_df(data, compact_to_dense, attributes):
    first_rows = [int(indices[0]) for indices in compact_to_dense]
    return data.iloc[first_rows][attributes].reset_index(drop=True)
