import numpy as np
import pandas as pd
from shared.entities.denial_constraints import Predicate

class PandasEngine:
    def find_constant_implication(self, data, u1, u2, p: Predicate) -> pd.DataFrame:
        m1, m2 = self.get_mask(data, u1), self.get_mask(data, u2)
        if not m1.any() or not m2.any():
            return pd.DataFrame(columns=['idx1', 'idx2'])
        
        idx1, idx2 = np.where(m1)[0], np.where(m2)[0]
        if not p:
            ii, jj = np.meshgrid(idx1, idx2)
            return pd.DataFrame({'idx1': ii.ravel(), 'idx2': jj.ravel()})

        return self._find_with_predicate(data, idx1, idx2, p)

    def find_fd_partitioned(self, data, eq_keys, u1, u2, attr) -> pd.DataFrame:
        m1, m2 = self.get_mask(data, u1), self.get_mask(data, u2)
        if not m1.any() or not m2.any():
            return pd.DataFrame(columns=['idx1', 'idx2'])
        
        relevant = m1 | m2
        sub = data[relevant].copy()
        sub['__idx'], sub['__m1'], sub['__m2'] = sub.index, m1[relevant], m2[relevant]
        
        if eq_keys:
            sub = sub[sub.groupby(eq_keys)[attr].transform('nunique') > 1]
        elif sub[attr].nunique() <= 1:
            return pd.DataFrame(columns=['idx1', 'idx2'])

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
        res = []
        for v1, ids1 in g1.items():
            for v2, ids2 in g2.items():
                if self._evaluate_scalar(v1, v2, opr):
                    ii, jj = np.meshgrid(ids1.values, ids2.values)
                    res.append(pd.DataFrame({'idx1': ii.ravel(), 'idx2': jj.ravel()}))
        return pd.concat(res) if res else pd.DataFrame(columns=['idx1', 'idx2'])

    def _evaluate_scalar(self, v1, v2, opr):
        if opr in ["=", "=="]: return v1 == v2
        if opr in ["!=", "<>"]: return v1 != v2
        if opr == ">": return v1 > v2
        if opr == ">=": return v1 >= v2
        if opr == "<": return v1 < v2
        if opr == "<=": return v1 <= v2
        return False

    def _process_groups(self, sub, eq_keys, attr):
        res = []
        all_groups = sub.groupby(eq_keys) if eq_keys else [(None, sub)]
        for _, group in all_groups:
            res.extend(self._process_fd_group(group, attr))
        return pd.concat(res) if res else pd.DataFrame(columns=['idx1', 'idx2'])

    def _process_fd_group(self, group, attr):
        res = []
        val_parts = group.groupby(attr)
        v_list = list(val_parts.groups.keys())
        for i in range(len(v_list)):
            g1 = val_parts.get_group(v_list[i])
            for j in range(i + 1, len(v_list)):
                g2 = val_parts.get_group(v_list[j])
                res.extend(self._generate_cross_pairs(g1, g2))
        return res

    def _generate_cross_pairs(self, g1, g2):
        res = []
        for (ga, gb) in [(g1, g2), (g2, g1)]:
            ids_a = ga.loc[ga['__m1'], '__idx'].values
            ids_b = gb.loc[gb['__m2'], '__idx'].values
            if len(ids_a) > 0 and len(ids_b) > 0:
                ii, jj = np.meshgrid(ids_a, ids_b)
                res.append(pd.DataFrame({'idx1': ii.ravel(), 'idx2': jj.ravel()}))
        return res
