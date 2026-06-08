import numpy as np
import pandas as pd

from u_utilities.u_shared import CompactData, Violation, ViolationSet

from .analyzer import ConstraintProfile, ConstraintType
from .utils import apply_unary_predicates


class OrderEngine:
    def find_violations(self, compact: CompactData, profile: ConstraintProfile) -> ViolationSet:
        match profile.type:
            case ConstraintType.TWO_ORDER:
                return self._find_two_order(compact, profile)
            case _:
                return self._find_single_order(compact, profile)

    def _find_single_order(self, compact: CompactData, profile: ConstraintProfile) -> ViolationSet:
        vs = compact.to_violation_set()
        predicate = profile.binary_predicates[0]
        left = self._order_frame(compact.df, profile.t1_unary, predicate.left.attr)
        right = self._order_frame(compact.df, profile.t2_unary, predicate.right.attr, sort=True)
        self._add_single_order_ranges(left, right, predicate, vs)
        self._add_internal_conflicts(compact, profile, vs)
        return vs

    def _find_two_order(self, compact: CompactData, profile: ConstraintProfile) -> ViolationSet:
        vs = compact.to_violation_set()
        df = compact.df
        left_ids = np.flatnonzero(apply_unary_predicates(df, profile.t1_unary))
        right_ids = np.flatnonzero(apply_unary_predicates(df, profile.t2_unary))
        values = {attr: pd.to_numeric(df[attr], errors="coerce").to_numpy() for attr in profile.order_attrs}
        for cid in left_ids:
            matches = self._two_order_matches(cid, right_ids, profile.binary_predicates, values)
            if len(matches):
                vs.conflicts.append(Violation(np.array([cid]), matches))
        return vs

    def _order_frame(self, df: pd.DataFrame, predicates, attr: str, sort: bool = False):
        mask = apply_unary_predicates(df, predicates)
        values = pd.to_numeric(df.loc[mask, attr], errors="coerce")
        frame = pd.DataFrame({"_cid": np.flatnonzero(mask), "_value": values})
        frame = frame.dropna(subset=["_value"])
        return frame.sort_values("_value") if sort else frame

    def _add_single_order_ranges(self, left, right, predicate, vs) -> None:
        right_ids = right["_cid"].to_numpy(dtype=int)
        right_values = right["_value"].to_numpy()
        for cid, value in left[["_cid", "_value"]].itertuples(index=False):
            start, end = self._range_for(predicate.opr, value, right_values)
            self._add_without_self(vs, int(cid), start, end, right_ids)

    def _range_for(self, operator: str, value, values: np.ndarray) -> tuple[int, int]:
        match operator:
            case ">":
                return 0, np.searchsorted(values, value, side="left")
            case ">=":
                return 0, np.searchsorted(values, value, side="right")
            case "<":
                return np.searchsorted(values, value, side="right"), len(values)
            case "<=":
                return np.searchsorted(values, value, side="left"), len(values)

    def _two_order_matches(self, cid: int, candidates, predicates, values) -> np.ndarray:
        mask = candidates != cid
        for predicate in predicates:
            left = values[predicate.left.attr][cid]
            right = values[predicate.right.attr][candidates]
            mask &= self._compare(left, predicate.opr, right) & ~np.isnan(right)
        valid_left = all(not np.isnan(values[p.left.attr][cid]) for p in predicates)
        return candidates[mask & valid_left].astype(int)

    def _compare(self, left, operator: str, right):
        match operator:
            case ">":
                return left > right
            case ">=":
                return left >= right
            case "<":
                return left < right
            case "<=":
                return left <= right

    def _add_without_self(self, vs, cid: int, start: int, end: int, right_ids) -> None:
        if start >= end:
            return
        matches = np.flatnonzero(right_ids[start:end] == cid)
        if len(matches) == 0:
            vs.conflicts.append(Violation(np.array([cid]), right_ids[start:end]))
            return
        split = start + int(matches[0])
        if start < split:
            vs.conflicts.append(Violation(np.array([cid]), right_ids[start:split]))
        if split + 1 < end:
            vs.conflicts.append(Violation(np.array([cid]), right_ids[split + 1 : end]))

    def _add_internal_conflicts(self, compact, profile, vs) -> None:
        if profile.binary_predicates[0].opr not in (">=", "<="):
            return
        both = apply_unary_predicates(compact.df, profile.t1_unary + profile.t2_unary)
        for cid in np.flatnonzero(both):
            if len(compact._compact_to_dense[int(cid)]) > 1:
                vs.conflicts.append(Violation(np.array([int(cid)]), np.array([int(cid)]), symmetric=True))
