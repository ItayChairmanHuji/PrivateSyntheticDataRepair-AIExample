from __future__ import annotations

from pandas import DataFrame

from u_utilities.u_shared import CompactData, Dataset, DenialConstraint, DenialConstraints, ViolationSet

from .analyzer import ConstraintAnalyzer, ConstraintType
from .conditional_constant_engine import ConditionalConstantEngine
from .duckdb_engine import DuckDBEngine
from .fd_engine import FDEngine
from .order_engine import OrderEngine


class ViolationFinder:
    def __init__(self, analyzer=None, fd_engine=None, order_engine=None, cc_engine=None, duckdb_engine=None):
        self.analyzer = analyzer or ConstraintAnalyzer()
        self.fd_engine = fd_engine or FDEngine()
        self.order_engine = order_engine or OrderEngine()
        self.cc_engine = cc_engine or ConditionalConstantEngine()
        self.duckdb_engine = duckdb_engine or DuckDBEngine()

    def find_violations(self, data: Dataset) -> ViolationSet:
        return self._find_dataset_violations(data) if len(data) else ViolationSet(cluster_indices=[])

    def _find_dataset_violations(self, dataset: Dataset) -> ViolationSet:
        compact = dataset.compact()
        violations = compact.to_violation_set()
        for dc in dataset.dcs.constraints:
            violations.violations.extend(self._find_dc_violations(compact, dc).violations)
        return violations

    def _find_dc_violations(self, compact: CompactData, dc: DenialConstraint) -> ViolationSet:
        profile = self.analyzer.analyze(dc)
        match profile.type:
            case ConstraintType.FD:
                return self.fd_engine.find_violations(compact, profile)
            case ConstraintType.CONDITIONAL_CONSTANT:
                return self.cc_engine.find_violations(compact, profile)
            case ConstraintType.SINGLE_ORDER | ConstraintType.TWO_ORDER:
                return self.order_engine.find_violations(compact, profile)
            case _:
                return self.duckdb_engine.find_violations_for_compact(dc, compact)
