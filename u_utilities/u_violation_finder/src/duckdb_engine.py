import logging

import duckdb
import numpy as np

from u_utilities.u_shared import CompactData, DenialConstraint, Violation, ViolationSet

from .duckdb_sql import DuckDBSqlBuilder

logger = logging.getLogger(__name__)


class DuckDBEngine:
    def __init__(self, sql_builder: DuckDBSqlBuilder | None = None):
        self.con = duckdb.connect(database=":memory:")
        self.sql = sql_builder or DuckDBSqlBuilder()

    def find_violations_for_compact(self, dc: DenialConstraint, compact: CompactData) -> ViolationSet:
        vs = compact.to_violation_set()
        self._register_clusters(dc, compact)
        self._add_pairwise_conflicts(dc, vs)
        self._add_internal_conflicts(dc, compact, vs)
        return vs

    def _register_clusters(self, dc: DenialConstraint, compact: CompactData) -> None:
        df = compact.df[list(dc.attrs)].copy()
        df["_cid"] = np.arange(len(compact.df))
        self.con.register("clusters", df)

    def _add_pairwise_conflicts(self, dc: DenialConstraint, vs: ViolationSet) -> None:
        result = self._query(self.sql.pairwise_sql(dc), dc)
        if result.empty:
            return
        for cid1, group in result.groupby("cid1"):
            vs.violations.append(Violation(np.array([int(cid1)]), group["cid2"].to_numpy(dtype=int)))

    def _add_internal_conflicts(self, dc: DenialConstraint, compact: CompactData, vs) -> None:
        result = self._query(self.sql.internal_sql(dc), dc)
        for cid in result.get("_cid", []):
            cid = int(cid)
            if len(compact._compact_to_dense[cid]) > 1:
                vs.violations.append(Violation(np.array([cid]), np.array([cid]), symmetric=True))

    def _query(self, sql: str, dc: DenialConstraint):
        try:
            return self.con.execute(sql).fetchdf()
        except Exception as error:
            logger.error("DuckDB error for DC %s: %s\nSQL: %s", dc.to_string(), error, sql)
            return self.con.execute("SELECT 1 WHERE FALSE").fetchdf()
