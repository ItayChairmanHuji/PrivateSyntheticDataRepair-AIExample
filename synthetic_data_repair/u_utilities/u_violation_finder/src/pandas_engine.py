import numpy as np
import pandas as pd
from u_utilities.u_shared import Predicate, BicliqueCollection

class PandasEngine:
    def find_constant_implication(self, data, u1, u2, p: Predicate) -> BicliqueCollection:
        m1, m2 = self.get_mask(data, u1), self.get_mask(data, u2)
        bc = BicliqueCollection()
        if not m1.any() or not m2.any():
            return bc
        
        idx1, idx2 = np.where(m1)[0], np.where(m2)[0]
        if not p:
            bc.add(idx1, idx2)
            return bc

        return self._find_with_predicate(data, idx1, idx2, p)

    def find_fd_partitioned(self, data, eq_keys, u1, u2, attr) -> BicliqueCollection:
        m1, m2 = self.get_mask(data, u1), self.get_mask(data, u2)
        bc = BicliqueCollection()
        if not m1.any() or not m2.any():
            return bc
        
        relevant = m1 | m2
        sub = data[relevant].copy()
        sub['__idx'], sub['__m1'], sub['__m2'] = sub.index, m1[relevant], m2[relevant]
        
        if eq_keys:
            sub = sub[sub.groupby(eq_keys)[attr].transform('nunique') > 1]
        elif sub[attr].nunique() <= 1:
            return bc

        return self._process_groups(sub, eq_keys, attr)

    def get_mask(self, data, predicates):
        mask = np.ones(len(data), dtype=bool)
        for p in predicates:
            mask &= self._apply_predicate(data, p)
        return mask

    def _apply_predicate(self, data, p):
        attr, raw_val = self._extract_attr_val(p)
        val = self._cast_val(data[attr].dtype, raw_val)
        return self._evaluate(data[attr], val, p.opr)

    def _extract_attr_val(self, p):
        if not p.left.is_value:
            return p.left.attr, p.right.attr
        return p.right.attr, p.left.attr

    def _cast_val(self, dtype, raw_val):
        if pd.api.types.is_numeric_dtype(dtype):
            try: return float(raw_val)
            except ValueError: return raw_val
        return raw_val

    def _evaluate(self, series, val, opr):
        if opr == "=": return series == val
        if opr == "!=": return series != val
        if opr == "<": return series < val
        if opr == "<=": return series <= val
        if opr == ">": return series > val
        if opr == ">=": return series >= val
        return False

    def _find_with_predicate(self, data, idx1, idx2, p):
        attr, opr = p.left.attr, p.opr
        g1, g2 = data.iloc[idx1].groupby(attr).groups, data.iloc[idx2].groupby(attr).groups
        bc = BicliqueCollection()
        for v1, ids1 in g1.items():
            for v2, ids2 in g2.items():
                if self._evaluate_scalar(v1, v2, opr):
                    bc.add(ids1.values, ids2.values)
        return bc

    def _evaluate_scalar(self, v1, v2, opr):
        if opr in ["=", "=="]: return v1 == v2
        if opr in ["!=", "<>"]: return v1 != v2
        if opr == ">": return v1 > v2
        if opr == ">=": return v1 >= v2
        if opr == "<": return v1 < v2
        if opr == "<=": return v1 <= v2
        return False

    def _process_groups(self, sub, eq_keys, attr):
        bc = BicliqueCollection()
        all_groups = sub.groupby(eq_keys) if eq_keys else [(None, sub)]
        for _, group in all_groups:
            self._process_fd_group(group, attr, bc)
        return bc

    def _process_fd_group(self, group, attr, bc):
        val_parts = group.groupby(attr)
        v_list = list(val_parts.groups.keys())
        
        # Pre-extract IDs for each value
        ids_by_val_m1 = []
        ids_by_val_m2 = []
        for v in v_list:
            g = val_parts.get_group(v)
            ids_by_val_m1.append(g.loc[g['__m1'], '__idx'].values)
            ids_by_val_m2.append(g.loc[g['__m2'], '__idx'].values)
        
        # Total counts to allow slicing/concatenation without repeated work
        for i in range(len(v_list)):
            m1_ids = ids_by_val_m1[i]
            m2_ids = ids_by_val_m2[i]
            
            # (m1 at i) conflicts with (m2 at >i)
            others_m2 = np.concatenate(ids_by_val_m2[i+1:]) if i+1 < len(v_list) else np.array([])
            if len(m1_ids) > 0 and len(others_m2) > 0:
                bc.add(m1_ids, others_m2)
                
            # (m2 at i) conflicts with (m1 at >i)
            others_m1 = np.concatenate(ids_by_val_m1[i+1:]) if i+1 < len(v_list) else np.array([])
            if len(m2_ids) > 0 and len(others_m1) > 0:
                bc.add(m2_ids, others_m1)
