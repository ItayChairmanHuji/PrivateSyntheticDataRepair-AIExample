import numpy as np
import pandas as pd

class PredicateCategorizer:
    def categorize(self, dc):
        eq_keys, ineq_preds, u1, u2 = [], [], [], []
        for p in dc.predicates:
            if not p.is_unary:
                if p.opr in ["=", "=="] and p.left.attr == p.right.attr:
                    eq_keys.append(p.left.attr)
                else:
                    ineq_preds.append(p)
            else:
                if p.left.index == 1: u1.append(p)
                else: u2.append(p)
        return eq_keys, ineq_preds, u1, u2

class ResultNormalizer:
    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        i1, i2 = df['idx1'].values, df['idx2'].values
        df['idx1'] = np.minimum(i1, i2)
        df['idx2'] = np.maximum(i1, i2)
        return df[df['idx1'] != df['idx2']].drop_duplicates()
