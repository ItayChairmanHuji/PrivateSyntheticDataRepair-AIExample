import duckdb
import pandas as pd
from shared.entities.denial_constraints import DenialConstraint, Predicate, Side

class SqlEngine:
    def find_order_violations(self, data, eq_keys, u1, u2, ineq_preds):
        con = self._setup_db(data)
        query = self._build_order_query(eq_keys, u1, u2, ineq_preds)
        if not con.execute(f"SELECT EXISTS ({query} LIMIT 1)").fetchone()[0]:
            con.close()
            return pd.DataFrame(columns=['idx1', 'idx2'])
        res = con.execute(query).df()
        con.close()
        return res

    def find_general_violations(self, data, dc):
        con = self._setup_db(data)
        query = self._build_general_query(dc)
        res = con.execute(query).df()
        con.close()
        return res

    def _setup_db(self, data):
        con = duckdb.connect(database=':memory:')
        con.register('df', data)
        con.execute("CREATE TABLE dt AS SELECT *, row_number() OVER () - 1 as __idx FROM df")
        return con

    def _build_order_query(self, eq_keys, u1, u2, ineq_preds):
        t1_f = self._format_preds(u1, "t1")
        t2_f = self._format_preds(u2, "t2")
        where_f = " AND ".join([self._format_predicate_sql(p) for p in ineq_preds])
        join_on = " AND ".join([f"t1.{k}=t2.{k}" for k in eq_keys]) if eq_keys else "1=1"
        return f"""
            SELECT DISTINCT t1.__idx as idx1, t2.__idx as idx2 
            FROM dt t1 JOIN dt t2 ON {join_on} 
            WHERE t1.__idx != t2.__idx AND ({t1_f}) AND ({t2_f}) AND ({where_f})
        """

    def _build_general_query(self, dc):
        from shared.utils.violation_finder.utils import PredicateCategorizer
        eq, ineq, u1, u2 = PredicateCategorizer().categorize(dc)
        t1_f = self._format_preds(u1, "t1")
        t2_f = self._format_preds(u2, "t2")
        where_f = " AND ".join([self._format_predicate_sql(p) for p in ineq]) if ineq else "1=1"
        join_on = " AND ".join([f"t1.{k}=t2.{k}" for k in eq]) if eq else "1=1"
        return f"""
            SELECT DISTINCT t1.__idx as idx1, t2.__idx as idx2 
            FROM dt t1 JOIN dt t2 ON {join_on} 
            WHERE t1.__idx != t2.__idx AND ({t1_f}) AND ({t2_f}) AND ({where_f})
        """

    def _format_preds(self, preds, alias):
        return " AND ".join([self._format_predicate_sql(p, alias) for p in preds]) if preds else "1=1"

    def _format_predicate_sql(self, pred: Predicate, alias: str = None) -> str:
        left = self._format_side_sql(pred.left, alias)
        right = self._format_side_sql(pred.right, alias)
        return f"{left} {pred.opr} {right}"

    def _format_side_sql(self, s: Side, alias: str) -> str:
        if s.is_value:
            try:
                float(s.attr)
                return str(s.attr)
            except ValueError:
                return f"'{s.attr}'"
        return f"{alias}.{s.attr}" if alias else f"t{s.index}.{s.attr}"
