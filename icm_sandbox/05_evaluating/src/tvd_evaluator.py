import itertools
import numpy as np
import pandas as pd
from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class TwoWayTVDEvaluator(Evaluator):
    """
    Computes averaged TVD for all 2-way marginals between private data and (synthetic/repaired) data.
    """
    def evaluate(self, result: PipelineResult) -> dict:
        p_data = result.private_dataset.data
        s_data = result.synthetic_dataset.data
        r_data = result.repaired_dataset.data
        
        columns = p_data.columns
        pairs = list(itertools.combinations(columns, 2))
        
        if not pairs:
            return {"tvd_2way": {}}
            
        syn_tvds = []
        rep_tvds = []
        
        for attr1, attr2 in pairs:
            p_counts = p_data[[attr1, attr2]].value_counts(normalize=True)
            s_counts = s_data[[attr1, attr2]].value_counts(normalize=True)
            r_counts = r_data[[attr1, attr2]].value_counts(normalize=True)
            
            syn_tvds.append(self._calculate_tvd(p_counts, s_counts))
            rep_tvds.append(self._calculate_tvd(p_counts, r_counts))
            
        return {
            "tvd_2way": {
                "synthetic_avg": sum(syn_tvds) / len(syn_tvds),
                "repaired_avg": sum(rep_tvds) / len(rep_tvds)
            }
        }

    def _calculate_tvd(self, counts1: pd.Series, counts2: pd.Series) -> float:
        # Align the two series to have the same indices
        combined = pd.concat([counts1, counts2], axis=1).fillna(0.0)
        combined.columns = ['c1', 'c2']
        # TVD = 0.5 * sum(|p_i - q_i|)
        return 0.5 * np.sum(np.abs(combined['c1'] - combined['c2']))
