import itertools
import numpy as np
import pandas as pd
from typing import List, Tuple
from u_utilities.u_shared import Marginal, MarginalSet
from .calculator import MarginalCalculator
from .error import MarginalError

class TopKSelector:
    """Worker: Selects top-k marginals using DP exponential mechanism."""

    def __init__(self):
        self.calc = MarginalCalculator()
        self.err = MarginalError()

    def select(
        self, 
        p_data: pd.DataFrame, 
        s_data: pd.DataFrame, 
        k: int, 
        budget: float,
        rng: np.random.Generator,
        **kwargs
    ) -> List[Tuple]:
        """Selects top-k marginal candidates."""
        scale = self._calc_selection_noise_scale(p_data, k, budget)
        candidates = self._gather_candidates(p_data, s_data, scale, rng, **kwargs)
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [(c[1], c[2]) for c in candidates[:k]]

    def _calc_selection_noise_scale(self, p_data, k, budget):
        sensitivity = self.err.sensitivity(p_data)
        return 2 * sensitivity * np.sqrt(k / (8 * budget))

    def _gather_candidates(self, p_data, s_data, scale, rng, **kwargs):
        candidates = []
        columns = self._filter_columns(p_data.columns, **kwargs)
        for attr1, attr2 in itertools.combinations(columns, 2):
            if self._should_skip(attr1, attr2, **kwargs):
                continue
            self._process_pair(p_data, s_data, attr1, attr2, scale, rng, candidates)
        return candidates

    def _filter_columns(self, columns, **kwargs):
        exclude = kwargs.get("exclude_attrs", [])
        return [c for c in columns if c not in exclude]

    def _should_skip(self, attr1, attr2, **kwargs):
        target = kwargs.get("target_attr")
        force = kwargs.get("force_target", True)
        if force and target and attr1 != target and attr2 != target:
            return True
        return False

    def _process_pair(self, p_data, s_data, attr1, attr2, scale, rng, candidates):
        p_vals, s_vals, indices = self.calc.align_frequencies(p_data, s_data, (attr1, attr2))
        if len(p_vals) == 0: return
        noisy_utils = self.err.compute(p_vals, s_vals) + rng.gumbel(0, scale, len(p_vals))
        for i, idx in enumerate(indices):
            candidates.append((noisy_utils[i], (attr1, attr2, idx[0], idx[1]), p_vals[i]))
