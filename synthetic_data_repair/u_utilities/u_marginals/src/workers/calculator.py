import pandas as pd
import numpy as np
from typing import Tuple, List
from u_utilities.u_shared import Marginal, MarginalSet

class MarginalCalculator:
    """Worker: Computes counts and frequencies for specified attribute sets."""

    def compute_frequencies(
        self, 
        data: pd.DataFrame, 
        attr_pair: Tuple[str, str]
    ) -> pd.Series:
        """Computes normalized frequencies for a pair of attributes."""
        return data[list(attr_pair)].value_counts(normalize=True)

    def align_frequencies(
        self, 
        p_data: pd.DataFrame, 
        s_data: pd.DataFrame, 
        attr_pair: Tuple[str, str]
    ) -> Tuple[np.ndarray, np.ndarray, pd.Index]:
        """Aligns frequencies between two datasets for a given attribute pair."""
        p_counts = self.compute_frequencies(p_data, attr_pair)
        s_counts = self.compute_frequencies(s_data, attr_pair)
        idx = p_counts.index.union(s_counts.index)
        p_vals = p_counts.reindex(idx, fill_value=0.0).values
        s_vals = s_counts.reindex(idx, fill_value=0.0).values
        return p_vals, s_vals, idx
