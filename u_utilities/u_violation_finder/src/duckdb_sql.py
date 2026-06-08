from u_utilities.u_shared import DenialConstraint, Predicate, Side


class DuckDBSqlBuilder:
    def pairwise_sql(self, dc: DenialConstraint) -> str:
        equality, where = self._partition(dc.predicates)
        return f"""
        SELECT DISTINCT
            LEAST(t1._cid, t2._cid) AS cid1,
            GREATEST(t1._cid, t2._cid) AS cid2
        FROM {self._from_clause(equality)}
        WHERE {self._where_clause(where)}
          AND t1._cid != t2._cid
        """

    def internal_sql(self, dc: DenialConstraint) -> str:
        where = [self._predicate_sql(p, "t1", "t1") for p in dc.predicates]
        return f"SELECT _cid FROM clusters t1 WHERE {self._where_clause(where)}"

    def _partition(self, predicates: list[Predicate]) -> tuple[list[Predicate], list[str]]:
        equality, where = [], []
        for predicate in predicates:
            if self._is_join_equality(predicate):
                equality.append(predicate)
            else:
                where.append(self._where_sql(predicate))
        return equality, where

    def _where_sql(self, predicate: Predicate) -> str:
        if not predicate.is_unary:
            return self._predicate_sql(predicate, "t1", "t2")
        table = "t1" if predicate.left.index == 1 else "t2"
        return self._predicate_sql(predicate, table, table)

    def _from_clause(self, equality: list[Predicate]) -> str:
        if not equality:
            return "clusters t1, clusters t2"
        conditions = [f"t1.{p.left.attr} IS NOT DISTINCT FROM t2.{p.left.attr}" for p in equality]
        return f"clusters t1 JOIN clusters t2 ON {' AND '.join(conditions)}"

    def _where_clause(self, predicates: list[str]) -> str:
        return " AND ".join(predicates) if predicates else "TRUE"

    def _is_join_equality(self, predicate: Predicate) -> bool:
        return not predicate.is_unary and predicate.opr in ("=", "==") and predicate.left.attr == predicate.right.attr

    def _predicate_sql(self, predicate: Predicate, t1_name: str, t2_name: str) -> str:
        left = self._side_sql(predicate.left, t1_name, t2_name)
        right = self._side_sql(predicate.right, t1_name, t2_name)
        match predicate.opr:
            case "==" | "=":
                return f"{left} IS NOT DISTINCT FROM {right}"
            case "!=" | "<>":
                return f"{left} IS DISTINCT FROM {right}"
            case operator:
                return f"{left} {operator} {right}"

    def _side_sql(self, side: Side, t1_name: str, t2_name: str) -> str:
        if side.is_value:
            return self._literal_sql(side.attr)
        return f"{t1_name if side.index == 1 else t2_name}.{side.attr}"

    def _literal_sql(self, value) -> str:
        if not isinstance(value, str):
            return str(value)
        return "'" + value.replace("'", "''") + "'"
