from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CompactData:
    df: pd.DataFrame
    _compact_to_dense: list[np.ndarray]
    _dense_to_compact: np.ndarray
    attributes: list[str]

    def to_violation_set(self) -> 'ViolationSet':
        from .violations import ViolationSet
        return ViolationSet(
            row_to_cluster=self._dense_to_compact,
            cluster_indices=self._compact_to_dense
        )

   ## TODO: Add save and load methods