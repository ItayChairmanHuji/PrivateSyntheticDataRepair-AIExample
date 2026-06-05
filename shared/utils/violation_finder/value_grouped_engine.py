import numpy as np
import pandas as pd
from shared.entities.denial_constraints import DenialConstraint, Predicate
from shared.entities.violations import BicliqueCollection
from shared.utils.violation_finder.utils import PredicateCategorizer

class ValueGroupedEngine:
    def __init__(self):
        self.categorizer = PredicateCategorizer()

    def find_violations(self, data: pd.DataFrame, dc: DenialConstraint) -> BicliqueCollection:
        # 1. Categorize predicates
        eq_keys, ineq_preds, u1, u2 = self.categorizer.categorize(dc)
        
        # Identify all attributes used in the DC
        all_cols = set()
        for p in dc.predicates:
            if not p.left.is_value: all_cols.add(p.left.attr)
            if not p.right.is_value: all_cols.add(p.right.attr)
        relevant_cols = sorted(list(all_cols))
        if not relevant_cols: return BicliqueCollection()

        # 2. Global grouping for biclique setup
        gb_all = data.groupby(relevant_cols, dropna=False)
        all_groups_dict = gb_all.indices
        unique_vals = list(all_groups_dict.keys())
        group_indices = [all_groups_dict[v] for v in unique_vals]
        
        bc = BicliqueCollection(group_indices=group_indices)
        row_to_group = np.zeros(len(data), dtype=int)
        for g_idx, indices in enumerate(group_indices):
            row_to_group[indices] = g_idx
        bc.row_to_group = row_to_group

        # Mapping from global unique values to their global group index
        val_to_gidx = {val: i for i, val in enumerate(unique_vals)}

        # 3. Partitioning by Equality Keys
        if eq_keys:
            # Group unique values by equality keys
            val_df = pd.DataFrame(unique_vals, columns=relevant_cols)
            partition_gb = val_df.groupby(eq_keys, dropna=False)
            
            for _, partition_indices in partition_gb.groups.items():
                self._check_groups(partition_indices, val_df, dc, bc, group_indices)
        else:
            # No equality keys, must check all pairs of groups
            self._check_groups(range(len(unique_vals)), pd.DataFrame(unique_vals, columns=relevant_cols), dc, bc, group_indices)
                    
        return bc

    def _check_groups(self, group_subset_indices, val_df, dc, bc, group_indices):
        """Checks violations within a subset of groups (a partition) using vectorization."""
        subset_len = len(group_subset_indices)
        if subset_len == 0: return

        # Extract values for the relevant columns in this partition
        relevant_cols = list(val_df.columns)
        subset_df = val_df.iloc[group_subset_indices][relevant_cols]
        
        # 1. Evaluate Internal Violations (i, i)
        # For internal violations, row1=row2.
        # This is a 1D check across all groups in the subset.
        internal_mask = np.ones(subset_len, dtype=bool)
        for p in dc.predicates:
            v1 = subset_df[p.left.attr].values if not p.left.is_value else p.left.attr
            v2 = subset_df[p.right.attr].values if not p.right.is_value else p.right.attr
            internal_mask &= self._vector_eval(v1, v2, p.opr)
        
        for idx, is_viol in enumerate(internal_mask):
            if is_viol:
                g_idx = group_subset_indices[idx]
                if len(group_indices[g_idx]) > 1:
                    bc.add_group_violation(g_idx, g_idx)

        # 2. Evaluate Pairwise Violations (i, j)
        # We need to check dc(row_i, row_j) OR dc(row_j, row_i)
        # Using broadcasting to get all pairs. 
        # Note: If subset_len is very large (e.g. > 10,000), this might hit memory limits.
        # But for 5700 (Tax case), 5700^2 is 32M elements, which is manageable.
        
        # Initialize masks for dc(i, j) and dc(j, i)
        mask_ij = np.ones((subset_len, subset_len), dtype=bool)
        mask_ji = np.ones((subset_len, subset_len), dtype=bool)
        
        for p in dc.predicates:
            v1 = subset_df[p.left.attr].values if not p.left.is_value else p.left.attr
            v2 = subset_df[p.right.attr].values if not p.right.is_value else p.right.attr
            
            # Broadcast to pairs
            # v1[:, None] is (N, 1), v2[None, :] is (1, N)
            # Result of eval is (N, N)
            res_ij = self._vector_eval(v1[:, None], v2[None, :], p.opr)
            res_ji = self._vector_eval(v2[:, None], v1[None, :], p.opr)
            
            mask_ij &= res_ij
            mask_ji &= res_ji
            
        # Combine and extract upper triangle indices (i < j)
        total_mask = mask_ij | mask_ji
        rows, cols = np.where(np.triu(total_mask, k=1))
        
        for r, c in zip(rows, cols):
            bc.add_group_violation(group_subset_indices[r], group_subset_indices[c])

    def _vector_eval(self, v1, v2, opr):
        if opr in ["=", "=="]: return v1 == v2
        if opr in ["!=", "<>"]: return v1 != v2
        if opr == "<": return v1 < v2
        if opr == "<=": return v1 <= v2
        if opr == ">": return v1 > v2
        if opr == ">=": return v1 >= v2
        return np.zeros_like(v1, dtype=bool)


    def _evaluate_dc(self, row1, row2, dc: DenialConstraint) -> bool:
        """Returns True if (row1, row2) satisfies the condition inside not(...)"""
        for p in dc.predicates:
            if not self._evaluate_predicate(row1, row2, p):
                return False
        return True

    def _evaluate_predicate(self, row1, row2, p: Predicate) -> bool:
        v1 = self._get_side_value(row1, row2, p.left)
        v2 = self._get_side_value(row1, row2, p.right)
        
        opr = p.opr
        if opr in ["=", "=="]: return v1 == v2
        if opr in ["!=", "<>"]: return v1 != v2
        if opr == "<": return v1 < v2
        if opr == "<=": return v1 <= v2
        if opr == ">": return v1 > v2
        if opr == ">=": return v1 >= v2
        return False

    def _get_side_value(self, row1, row2, side):
        if side.is_value:
            try: return float(side.attr)
            except ValueError: return side.attr
        
        row = row1 if side.index == 1 else row2
        return row[side.attr]
