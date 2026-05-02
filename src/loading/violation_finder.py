import pandas as pd
import duckdb
import numpy as np
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

class ViolationFinder:
    def find_violations(self, data: pd.DataFrame, dcs: DenialConstraints) -> pd.DataFrame:
        if len(data) == 0 or len(dcs.constraints) == 0:
            return pd.DataFrame(columns=['idx1', 'idx2'])

        all_violations = []
        for dc in dcs.constraints:
            try:
                result = self._find_violations_optimized(data, dc)
                if not result.empty:
                    all_violations.append(result)
            except Exception as e:
                print(f"Error processing DC {dc.to_string()}: {e}")

        if not all_violations:
            return pd.DataFrame(columns=['idx1', 'idx2'])

        combined = pd.concat(all_violations)
        return self._normalize_and_deduplicate(combined).reset_index(drop=True)

    def _normalize_and_deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        i1 = df['idx1'].values
        i2 = df['idx2'].values
        # 1. Enforce idx1 < idx2
        df['idx1'] = np.minimum(i1, i2)
        df['idx2'] = np.maximum(i1, i2)
        # 2. Ignore self-conflicts
        df = df[df['idx1'] != df['idx2']]
        # 3. Deduplicate
        return df.drop_duplicates()

    def _find_violations_optimized(self, data: pd.DataFrame, dc: DenialConstraint) -> pd.DataFrame:
        eq_keys, ineq_preds, u1, u2 = self._categorize_predicates(dc)
        
        # --- Pattern 1: Constant-Value Implication (Pandas) ---
        if not eq_keys and len(ineq_preds) <= 1:
            return self._find_constant_implication_pandas(data, u1, u2, ineq_preds[0] if ineq_preds else None)

        # --- Pattern 2: Standard or Conditional FD (Value-Partitioned Join) ---
        if len(ineq_preds) == 1 and ineq_preds[0].opr in ["!=", "<>"]:
            return self._find_fd_partitioned(data, eq_keys, u1, u2, ineq_preds[0].left.attr)

        # --- Pattern 3: Order Constraints (DuckDB - Surgical) ---
        if len(ineq_preds) >= 1:
            return self._find_order_duckdb(data, eq_keys, u1, u2, ineq_preds)

        # Fallback
        return self._find_general_duckdb(data, dc)

    def _categorize_predicates(self, dc: DenialConstraint):
        eq_keys, ineq_preds, u1, u2 = [], [], [], []
        for p in dc.predicates:
            if not p.is_unary:
                if p.opr in ["=", "=="] and p.left.attr == p.right.attr: eq_keys.append(p.left.attr)
                else: ineq_preds.append(p)
            else:
                if p.left.index == 1: u1.append(p)
                else: u2.append(p)
        return eq_keys, ineq_preds, u1, u2

    def _compare(self, v1, v2, opr):
        if opr in ["=", "=="]: return v1 == v2
        if opr in ["!=", "<>"]: return v1 != v2
        if opr == ">": return v1 > v2
        if opr == ">=": return v1 >= v2
        if opr == "<": return v1 < v2
        if opr == "<=": return v1 <= v2
        return False

    def _find_constant_implication_pandas(self, data, u1, u2, p: Predicate) -> pd.DataFrame:
        mask1 = self._get_pandas_mask(data, u1)
        mask2 = self._get_pandas_mask(data, u2)
        if not mask1.any() or not mask2.any(): return pd.DataFrame(columns=['idx1', 'idx2'])
        
        idx1, idx2 = np.where(mask1)[0], np.where(mask2)[0]
        if p:
            attr, opr = p.left.attr, p.opr
            sub1, sub2 = data.iloc[idx1], data.iloc[idx2]
            groups1 = sub1.groupby(attr).groups
            groups2 = sub2.groupby(attr).groups
            res = []
            for v1, ids1 in groups1.items():
                for v2, ids2 in groups2.items():
                    if self._compare(v1, v2, opr):
                        ii, jj = np.meshgrid(ids1.values, ids2.values)
                        res.append(pd.DataFrame({'idx1': ii.ravel(), 'idx2': jj.ravel()}))
            return pd.concat(res) if res else pd.DataFrame(columns=['idx1', 'idx2'])
        else:
            ii, jj = np.meshgrid(idx1, idx2)
            return pd.DataFrame({'idx1': ii.ravel(), 'idx2': jj.ravel()})

    def _find_fd_partitioned(self, data, eq_keys, u1, u2, attr) -> pd.DataFrame:
        m1, m2 = self._get_pandas_mask(data, u1), self._get_pandas_mask(data, u2)
        if not m1.any() or not m2.any(): return pd.DataFrame(columns=['idx1', 'idx2'])
        
        relevant_mask = m1 | m2
        sub = data[relevant_mask].copy()
        sub['__idx'] = sub.index
        sub['__m1'] = m1[relevant_mask]
        sub['__m2'] = m2[relevant_mask]
        
        if eq_keys:
            mask = sub.groupby(eq_keys)[attr].transform('nunique') > 1
            sub = sub[mask]
        elif sub[attr].nunique() <= 1:
            return pd.DataFrame(columns=['idx1', 'idx2'])

        if sub.empty: return pd.DataFrame(columns=['idx1', 'idx2'])

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

    def _find_order_duckdb(self, data, eq_keys, u1, u2, ineq_preds) -> pd.DataFrame:
        con = duckdb.connect(database=':memory:')
        con.register('df', data)
        con.execute("CREATE TABLE dt AS SELECT *, row_number() OVER () - 1 as __idx FROM df")
        
        t1_f = " AND ".join([self._format_predicate_sql(p, "t1") for p in u1]) if u1 else "1=1"
        t2_f = " AND ".join([self._format_predicate_sql(p, "t2") for p in u2]) if u2 else "1=1"
        where_f = " AND ".join([self._format_predicate_sql(p) for p in ineq_preds])
        join_on = " AND ".join([f"t1.{k}=t2.{k}" for k in eq_keys]) if eq_keys else "1=1"
        
        query = f"""
            SELECT DISTINCT 
                t1.__idx as idx1, 
                t2.__idx as idx2 
            FROM dt t1 JOIN dt t2 ON {join_on} 
            WHERE t1.__idx != t2.__idx AND ({t1_f}) AND ({t2_f}) AND ({where_f})
        """
        
        has_v = con.execute(f"SELECT EXISTS ({query} LIMIT 1)").fetchone()[0]
        if not has_v: 
            con.close()
            return pd.DataFrame(columns=['idx1', 'idx2'])

        res = con.execute(query).df()
        con.close()
        return res

    def _find_general_duckdb(self, data, dc) -> pd.DataFrame:
        con = duckdb.connect(database=':memory:')
        con.register('df', data)
        con.execute("CREATE TABLE dt AS SELECT *, row_number() OVER () - 1 as __idx FROM df")
        eq, ineq, u1, u2 = self._categorize_predicates(dc)
        t1_f = " AND ".join([self._format_predicate_sql(p, "t1") for p in u1]) if u1 else "1=1"
        t2_f = " AND ".join([self._format_predicate_sql(p, "t2") for p in u2]) if u2 else "1=1"
        where_f = " AND ".join([self._format_predicate_sql(p) for p in ineq]) if ineq else "1=1"
        join_on = " AND ".join([f"t1.{k}=t2.{k}" for k in eq]) if eq else "1=1"
        
        query = f"""
            SELECT DISTINCT 
                t1.__idx as idx1, 
                t2.__idx as idx2 
            FROM dt t1 JOIN dt t2 ON {join_on} 
            WHERE t1.__idx != t2.__idx AND ({t1_f}) AND ({t2_f}) AND ({where_f})
        """
        res = con.execute(query).df()
        con.close()
        return res

    def _get_pandas_mask(self, data, predicates):
        mask = np.ones(len(data), dtype=bool)
        for p in predicates:
            val = float(p.right.attr) if p.right.is_value else float(p.left.attr)
            attr = p.left.attr if not p.left.is_value else p.right.attr
            if p.opr == "=": mask &= (data[attr] == val)
            elif p.opr == "!=": mask &= (data[attr] != val)
            elif p.opr == "<": mask &= (data[attr] < val)
            elif p.opr == "<=": mask &= (data[attr] <= val)
            elif p.opr == ">": mask &= (data[attr] > val)
            elif p.opr == ">=": mask &= (data[attr] >= val)
        return mask

    def _format_predicate_sql(self, pred: Predicate, alias: str = None) -> str:
        def format_side(s: Side) -> str:
            if s.is_value:
                try: float(s.attr); return str(s.attr)
                except ValueError: return f"'{s.attr}'"
            if alias: return f"{alias}.{s.attr}"
            return f"t{s.index}.{s.attr}"
        return f"{format_side(pred.left)} {pred.opr} {format_side(pred.right)}"
