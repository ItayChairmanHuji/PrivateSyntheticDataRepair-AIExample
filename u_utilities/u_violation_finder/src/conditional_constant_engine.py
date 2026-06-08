import pandas as pd

from u_utilities.u_shared import CompactData, Violation, ViolationSet

from .analyzer import ConstraintProfile
from .utils import apply_unary_predicates


class ConditionalConstantEngine:
    def find_violations(self, compact: CompactData, profile: ConstraintProfile) -> ViolationSet:
        vs = compact.to_violation_set()
        t1 = self._filtered_frame(compact.df, profile.t1_unary)
        t2 = self._filtered_frame(compact.df, profile.t2_unary)
        for left, right in self._paired_groups(t1, t2, profile.equality_attrs):
            self._add_neq_conflicts(left, right, profile.inequality_attrs[0], vs)
        return vs

    def _filtered_frame(self, df: pd.DataFrame, predicates) -> pd.DataFrame:
        mask = apply_unary_predicates(df, predicates)
        return df.loc[mask].assign(_cid=mask.nonzero()[0])

    def _paired_groups(self, t1: pd.DataFrame, t2: pd.DataFrame, keys: list[str]):
        if t1.empty or t2.empty:
            return []
        if not keys:
            return [(t1, t2)]
        return self._matching_groups(t1, t2, keys)

    def _matching_groups(self, t1: pd.DataFrame, t2: pd.DataFrame, keys: list[str]):
        right_groups = dict(tuple(t2.groupby(keys, dropna=False)))
        return ((left, right_groups[key]) for key, left in t1.groupby(keys, dropna=False) if key in right_groups)

    def _add_neq_conflicts(self, t1: pd.DataFrame, t2: pd.DataFrame, key: str, vs) -> None:
        right_groups = dict(tuple(t2.groupby(key, dropna=False)))
        for left_value, left in t1.groupby(key, dropna=False):
            for right_value, right in right_groups.items():
                if not self._same_value(left_value, right_value):
                    vs.conflicts.append(Violation(left["_cid"].to_numpy(), right["_cid"].to_numpy()))

    def _same_value(self, left, right) -> bool:
        return left == right or (pd.isna(left) and pd.isna(right))
