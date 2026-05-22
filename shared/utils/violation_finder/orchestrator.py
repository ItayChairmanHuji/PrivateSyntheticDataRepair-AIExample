import pandas as pd
from shared.entities.denial_constraints import DenialConstraints
from shared.utils.violation_finder.pandas_engine import PandasEngine
from shared.utils.violation_finder.sql_engine import SqlEngine
from shared.utils.violation_finder.utils import PredicateCategorizer, ResultNormalizer

class ViolationFinder:
    def __init__(self):
        self.pandas = PandasEngine()
        self.sql = SqlEngine()
        self.categorizer = PredicateCategorizer()
        self.normalizer = ResultNormalizer()

    def find_violations(self, data: pd.DataFrame, dcs: DenialConstraints) -> pd.DataFrame:
        if len(data) == 0 or len(dcs.constraints) == 0:
            return pd.DataFrame(columns=['idx1', 'idx2'])

        all_violations = []
        for dc in dcs.constraints:
            try:
                res = self._find_single_dc(data, dc)
                if not res.empty: all_violations.append(res)
            except Exception as e:
                print(f"Error processing DC {dc.to_string()}: {e}")

        if not all_violations:
            return pd.DataFrame(columns=['idx1', 'idx2'])

        combined = pd.concat(all_violations)
        return self.normalizer.normalize(combined).reset_index(drop=True)

    def _find_single_dc(self, data, dc):
        eq, ineq, u1, u2 = self.categorizer.categorize(dc)
        
        # Pattern 1: Constant-Value Implication (Pandas)
        if not eq and len(ineq) <= 1:
            return self.pandas.find_constant_implication(data, u1, u2, ineq[0] if ineq else None)

        # Pattern 2: FD (Value-Partitioned Join)
        if len(ineq) == 1 and ineq[0].opr in ["!=", "<>"]:
            return self.pandas.find_fd_partitioned(data, eq, u1, u2, ineq[0].left.attr)

        # Pattern 3: Order Constraints (DuckDB)
        if len(ineq) >= 1:
            return self.sql.find_order_violations(data, eq, u1, u2, ineq)

        return self.sql.find_general_violations(data, dc)
