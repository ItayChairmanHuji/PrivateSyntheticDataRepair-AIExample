from itertools import combinations

import numpy as np
import pandas as pd

from u_utilities.u_shared import CompactData, Violation, ViolationSet

from .analyzer import ConstraintProfile
from .utils import apply_unary_predicates


class FDEngine:
    def find_violations(self, compact: CompactData, profile: ConstraintProfile) -> ViolationSet:
        vs = compact.to_violation_set()
        active = self._active_frame(compact.df, profile.unary_predicates)
        for group in self._equality_groups(active, profile.equality_attrs):
            self._add_inequality_conflicts(group, profile.inequality_attrs[0], vs)
        return vs

    def _active_frame(self, df: pd.DataFrame, predicates) -> pd.DataFrame:
        mask = apply_unary_predicates(df, predicates)
        return df.loc[mask].assign(_cid=np.flatnonzero(mask))

    def _equality_groups(self, df: pd.DataFrame, keys: list[str]):
        if df.empty:
            return []
        if not keys:
            return [df]
        return (group for _, group in df.groupby(keys, dropna=False))

    def _add_inequality_conflicts(self, group: pd.DataFrame, key: str, vs: ViolationSet) -> None:
        subgroups = [part["_cid"].to_numpy() for _, part in group.groupby(key, dropna=False)]
        for left, right in combinations(subgroups, 2):
            vs.violations.append(Violation(left, right))
